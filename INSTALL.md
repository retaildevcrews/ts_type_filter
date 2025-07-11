# Installation Instructions

## Development Installation

To install this package in development mode:

1. Clone the repository:
   ```bash
   git clone https://github.com/MikeHopcroft/ts_type_filter.git
   cd ts_type_filter
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. In your target project, add the dependency using the local path:
   ```bash
   poetry add ../path/to/ts_type_filter
   ```

## Alternative Installation Methods

### Using pip with git URL
```bash
pip install git+https://github.com/MikeHopcroft/ts_type_filter.git
```

### Using Poetry with git URL (development branch)
```bash
poetry add git+https://github.com/MikeHopcroft/ts_type_filter.git
```

Note: The git URL installation requires that the repository has the proper package structure.
