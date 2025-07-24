# Reflection

`core.reflection` provides a placeholder `reflect` function to log outcomes and generate a simple lesson learned summary.

Call this after an attack simulation or agent action to record what happened:

```python
from core.reflection import reflect

lesson = reflect("success", "exploited service B")
print(lesson)
```
