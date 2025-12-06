# Utils Python Global

A miscellaneous collection of Python utility functions for personal development usage.

## Overview

This python repository contains various utility modules and helper functions that I frequently use across different projects. It's a personal toolkit that has grown organically over time to support various development needs.

## What's Inside

This collection includes utilities for:

- **Media File Processing**(`_utils_image/` and `_utils_exif/`) - Image processing, EXIF metadata handling
- **File System Operations**(`_utils_file/`) - File I/O, path management, YAML handling.
- **System**(`_utils_io/` and `_utils_system/`) - General system-level utilities and helpers
- **Math**(`_utils_math/`) - Mathematical utilities and computations
- **Neural Networks**(`_utils_nn/`) - PyTorch helpers, training utilities, model training
- **Plotting**(`_utils_plot/`) - Visualization and plotting utilities
- **VSCode snippets and templates**

## Usage
`_utils_import.py` is for accessing modules and classes in this repo. example:

```python
from _utils_import import List, Dict # lightweight wrapper for built-in list and dict class
from _utils_import import _utils_file
```