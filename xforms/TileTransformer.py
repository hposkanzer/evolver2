import mono_pil

# A special class that's the end-point of transformer chains when in tile mode.
# Input is a NonTransformer.
class TileTransformer(mono_pil.Shift):

    is_tile_transformer = 1
    is_reserved_transformer = 1

    def getPairs(self, prev=None):
        return []
