from guiqwt.curve import ItemListWidget
from guiqwt.curve import get_icon


def _patch_item_list():
    orig___get_item_icon = ItemListWidget._ItemListWidget__get_item_icon  # save the original method

    def custom_get_item_icon(self, item):
        try:
            icon_name = item.curveparam._DataSet__icon
            return get_icon(icon_name)
        except AttributeError:
            return orig___get_item_icon(self, item)

    # now monkey patch
    ItemListWidget._ItemListWidget__get_item_icon = custom_get_item_icon
