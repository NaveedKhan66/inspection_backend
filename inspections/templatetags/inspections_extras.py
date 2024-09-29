from django import template

register = template.Library()


@register.simple_tag
def get_home_address(deficiency):
    home = deficiency.home_inspection.home
    home_address = " ".join(
        [
            a
            for a in [
                home.lot_no if home.lot_no else "",
                home.address if home.address else "",
                home.postal_code if home.postal_code else "",
            ]
            if a
        ]
    )
    return home_address
