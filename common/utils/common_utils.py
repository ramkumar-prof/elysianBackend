import uuid

def get_rel_path(product_id, product_name, is_default):
    if is_default:
        return f"images/products/{product_name}_{product_id}/main"
    else:
        # uuid for random folder name
        folder_name = uuid.uuid4().hex[:8]
        return f"images/products/{product_name}_{product_id}/{folder_name}"
