from dataclasses import dataclass, asdict

@dataclass
class Test:
    x: int
    y: str = "default"

t = Test(x=5)
print("asdict():", asdict(t))
print("__dict__:", t.__dict__)
print("Are they equal?", asdict(t) == t.__dict__)
