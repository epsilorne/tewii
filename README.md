# 🥕 Tewii 

Tewii is a Pandoc wrapper surrounding your default text editor, allowing you to seamlessly create LaTeX documents, rendered as a PDF, all from simpler Markdown.

More doco TBA.

## Features

- Use your default text editor to edit Markdown files and see a rendered PDF from your default PDF viewer
- Automated Markdown -> LaTeX conversion and rendering, every time you save your files
- Support for multiple source files, all combined into a single rendered document

## Installation
Tewii requires [Pandoc](https://pandoc.org/) and `pdflatex` (included with any LaTeX distribution), as well as Python >= 3.14.

You can build from source using [UV](https://github.com/astral-sh/uv):

```bash
git clone https://github.com/epsilorne/tewii.git
cd tewii
uv install .
```

## Usage
Create an empty project using:
```
$ tewii init <NAME>
```

Then, edit your project with:
```
$ tewii edit <NAME>
```

For the best experience, it's recommended to use a PDF viewer that automatically refreshes upon file changes.
That way, changes in your source files are automatically reflected in the rendered PDF without intervening.
