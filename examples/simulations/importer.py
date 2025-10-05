import pkgutil, eigen
import eigen.robots
for mod in pkgutil.walk_packages(eigen.__path__, eigen.__name__ + "."):
    print(mod.name)
