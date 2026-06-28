# HossAgent Refactor Notes

Goal:
Turn the current working rescue-code monolith into a maintainable product codebase.

Pass 1:
- Preserve current behavior.
- Add modular package skeleton.
- Add route hygiene utility.
- Add route inventory endpoint.
- Keep latest registered route per path/method.
- Do not delete business logic yet.

Next:
- Move config routes.
- Move eval routes.
- Move market scan route.
- Move connector functions.
- Then delete old route generations from hoss_core.py.
