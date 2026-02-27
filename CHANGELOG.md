# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Fast Inference Server
- Binary protocol using Pickle Protocol 5 for efficient serialization
- Flask-based REST API with `/infer` and `/update_model` endpoints
- Client request utilities with automatic retry logic
- Hot model update without server restart
- Comprehensive documentation (English and Chinese)
- Development guide with customization examples
- Example usage scripts
- Apache License 2.0

### Features
- Support for numpy arrays and arbitrary Python objects
- Optimized data transfer with minimal overhead
- Single-threaded sequential processing for deterministic behavior
- Timeout and retry mechanism for robust client requests
- Secure tar file extraction with path traversal protection

### Documentation
- README with quick start guide
- Development guide with performance tuning tips
- Contributing guidelines
- Example usage scripts

## [1.0.0] - 2025-02-27

### Added
- Initial public release
