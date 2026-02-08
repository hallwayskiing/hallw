---
name: online-shopping
description: Workflow for shopping online. Use when the user needs to browse e-commerce sites, search products, compare items, add to cart, or complete purchases. Supports Amazon, eBay, and other major shopping platforms.
---

# Online Shopping Workflow

## Stages

1. **browse shopping website** - Navigate to store and search for products
2. **select product** - Browse and select desired items
3. **add to cart** - Add products to shopping cart

## Tool Sequence

```
build_stages(stage_names=['browse shopping website', 'select product', 'add to cart'])
cat USER.md
browser_goto(page_index=0, url='<shopping-website-url>')
browser_fill(page_index=0, element_id='<search-box-id>', text='<product-name>')
browser_click(page_index=0, element_id='<search-button-id>')
end_current_stage()

browser_click(page_index=0, element_id='<product-link-id>')
end_current_stage()

browser_click(page_index=0, element_id='<add-to-cart-button-id>')
exec(command='Set-Content -Path "workspace/order_confirmation.md" -Value "# Order Confirmation`n`nProduct: <product>`nDate: <date>"') # in Windows
exec(command='echo "# Order Confirmation`n`nProduct: <product>`nDate: <date>" > workspace/order_confirmation.md') # in Linux/Mac
end_current_stage()
```
