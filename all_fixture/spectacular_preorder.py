def reorder_operations_postprocessing(result, generator, request, public):
    # переупорядочиваем paths
    new_paths = {}
    paths = result["paths"]

    custom_order = [
        "/api/v1/tours/populars/",
        "/api/v1/tours/hots/",
        "/api/v1/hotels/hots/",
        "/api/v1/promocodes/",
        "/api/v1/promocodes/check/",
        "/api/v1/hotels/populars/",
    ]

    # сначала добавляем в нужном порядке
    for path in custom_order:
        if path in paths:
            new_paths[path] = paths[path]

    # затем все остальные
    for path, val in paths.items():
        if path not in new_paths:
            new_paths[path] = val

    result["paths"] = new_paths
    return result
