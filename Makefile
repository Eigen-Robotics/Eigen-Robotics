.PHONY: install sync clean help
EIGEN_TYPE_DEFS=packages/eigen_framework/src/eigen/types/eigen_type_defs
EIGEN_TYPE_DESTINATION=packages/eigen_framework/src
EIGEN_TYPES_COMPILED=packages/eigen_framework/src/eigen/types/generated
# One-command cross-platform setup
install:
ifeq ($(shell uname),Darwin)
	@echo "🍎 macOS detected";
	@echo "📦 Building PyBullet wheel (this may take a few minutes)...";
	@uv run ./scripts/build_pybullet_macos.py;
else
ifeq ($(shell uname),Linux)
	@echo "🐧 Linux detected"
else
	@echo "Unsupported platform."
	exit 1
endif
endif
	@echo "📦 Installing dependencies with uv..."
	@uv sync
	@echo "Installing lcm types..."
	@uv run lcm-gen -p --ppath $(EIGEN_TYPE_DESTINATION) $(EIGEN_TYPE_DEFS)/*
	@rm -f "packages/eigen_framework/src/eigen/__init__.py"
	@echo "✅ Setup complete!"


# Standard sync for daily use
sync:
	@uv sync

# Clean everything except built wheels
clean:
	@echo "🧹 Cleaning..."
	@rm -rf .venv dist/
	@rm -rf $(EIGEN_TYPES_COMPILED)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
# Clean everything
clea-all:
	@echo "🧹 Cleaning..."
	@rm -rf .venv dist wheels/
	@rm -rf $(EIGEN_TYPES_COMPILED)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
# Show available commands
help:
	@echo "Available commands:"
	@echo "  make install  		- First-time setup (builds PyBullet on macOS, installs a venv)"
	@echo "  make sync     		- Update dependencies"
	@echo "  make clean    		- Clean cache files"
	@echo "  make clean-all		- Clean cache files including built wheels"
	@echo ""
	@echo "After 'make install', you can use 'uv sync' directly"
