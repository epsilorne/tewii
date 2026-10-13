# Tewii 🥕
Tewii is a Pandoc wrapper, allowing you to seamlessly create LaTeX (+ Rendered PDF) documents, using simpler Markdown.

More doco TBA.

## Dependencies
- `pandoc`
- `pdflatex` (included with any LaTeX distro)
- `python` (>= `3.14`)
- `uv`

## Installation
```bash
git clone https://github.com/epsilorne/tewii.git
cd tewii
uv install .
```

## Usage
You can create an empty project using:
```
tewii init <NAME>
```

And then edit your project using:
```
tewii edit <NAME>
```

Tewii will open the project's source files in your preferred text editor, in addition to your `.pdf` viewer.
When changes are made, both a `.tex` and `.pdf` are generated, and previewed in the `.pdf` viewer.
