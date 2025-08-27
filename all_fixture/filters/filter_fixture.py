def filter_choices(model, field):
    try:
        return [
            (name, name) for name in model.objects.values_list(field, flat=True).distinct().order_by(field) if name
        ]
    except Exception:
        return []
