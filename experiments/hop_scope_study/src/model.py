"""Single intervention, inheriting immutable source-faithful GAMMA components.

MIT-derived components: research/src/model.py at target main 935a430;
upstream 36d054b4ae53c0c8e360d85d056f5207d61c8281. See repository NOTICE.
"""
import torch
from research.src.model import GammaLayer, GammaNet


def checked_mask(mask, hops):
    if mask.dtype != torch.bool or mask.shape != (hops.shape[1],):
        raise ValueError('Mask must be a boolean vector over all computed hops')
    if mask.device != hops.device:
        raise ValueError('Mask and embeddings must use the same device')
    if not bool(mask.any()):
        raise ValueError('At least one hop must remain active')
    return mask


class ScopeLayer(GammaLayer):
    def __init__(self, in_channels, out_channels, max_propagation_hop=5,
                 max_gating_hop=5, num_iterations=2):
        if max_propagation_hop != 5:
            raise ValueError('This registered study fixes max_propagation_hop=5')
        if type(max_gating_hop) is not int or not 1 <= max_gating_hop <= 5:
            raise ValueError('max_gating_hop must be an integer in 1..5')
        if num_iterations < 1:
            raise ValueError('Routing iterations must be positive')
        super().__init__(in_channels, out_channels, powers=range(6),
                         num_iterations=num_iterations, routing_score='dot')
        self.max_propagation_hop = max_propagation_hop
        self.max_gating_hop = max_gating_hop

    def set_scope(self, x):
        if type(x) is not int or not 1 <= x <= 5:
            raise ValueError('Invalid routing scope')
        self.max_gating_hop = x

    def route(self, hops, return_diagnostics=False):
        mask = checked_mask(torch.arange(6, device=hops.device) <= self.max_gating_hop, hops)
        # Preserve the original default float32 logits, including float64 parity.
        b = torch.zeros(hops.size(0), 6, device=hops.device)
        details = []
        for _ in range(self.num_iterations):
            alpha = torch.softmax(b.masked_fill(~mask.unsqueeze(0), -torch.inf), dim=1)
            fused = self.squash(torch.sum(alpha.unsqueeze(-1) * hops, dim=1))
            agreement = self.score(hops, fused)
            if return_diagnostics:
                details.append(dict(logits=b, alpha=alpha, fused=fused, agreement=agreement))
            b = b + agreement
        out = fused + self.bias
        if return_diagnostics:
            return out, dict(hops=hops, iterations=details, used_alpha=alpha,
                             post_update_logits=b, active_mask=mask)
        return out

    def forward(self, x, edge_index, edge_weight=None, return_diagnostics=False):
        # Inherited routine computes ALL six branches, 15 calls, at every scope.
        hops = self.hop_embeddings(x, edge_index, edge_weight)
        return self.route(hops, return_diagnostics)


class ScopeNet(GammaNet):
    def __init__(self, in_channels, hidden_channels, out_channels,
                 max_propagation_hop=5, max_gating_hop=5, num_iterations=2):
        # Build and retain exactly the original parameter initialization order.
        super().__init__(in_channels, hidden_channels, out_channels,
                         powers=range(6), num_layers=2, num_iterations=num_iterations)
        old = self.convs[0]
        # Changing Python class adds no parameters or RNG draws; inherited forward
        # normalization/dropout/head and the original state keys remain identical.
        old.__class__ = ScopeLayer
        old.max_propagation_hop = max_propagation_hop
        if max_propagation_hop != 5:
            raise ValueError('Fixed propagation must be 5')
        old.set_scope(max_gating_hop)

    def set_scope(self, x):
        for conv in self.convs:
            conv.set_scope(x)
