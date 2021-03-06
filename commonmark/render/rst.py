from __future__ import unicode_literals


from commonmark.render.renderer import Renderer


class ReStructuredTextRenderer(Renderer):
    """
    Render reStructuredText from Markdown

    Example:

    .. code:: python

        import commonmark

        parser = commonmark.Parser()
        ast = parser.parse('Hello `inline code` example')

        renderer = commonmark.ReStructuredTextRenderer()
        rst = renderer.render(ast)
        print(rst)  # Hello ``inline code`` example
    """
    def __init__(self, indent_char=' '):
        self.indent_char = indent_char
        self.indent_length = 0

    def lit(self, s):
        if s == '\n':
            indent = ''  # Avoid whitespace if we're just adding a newline
        elif self.last_out != '\n':
            indent = ''  # Don't indent if we're in the middle of a line
        else:
            indent = self.indent_char * self.indent_length

        return super(ReStructuredTextRenderer, self).lit(indent + s)

    def cr(self):
        self.lit('\n')

    def indent_lines(self, literal, indent_length=4):
        indent = self.indent_char * indent_length
        new_lines = []

        for line in literal.splitlines():
            new_lines.append(indent + line)

        return '\n'.join(new_lines)

    # Nodes

    def document(self, node, entering):
        pass

    def softbreak(self, node, entering):
        self.cr()

    def linebreak(self, node, entering):
        self.cr()
        self.cr()

    def text(self, node, entering):
        self.out(node.literal)

    def emph(self, node, entering):
        self.out('*')

    def strong(self, node, entering):
        self.out('**')

    def paragraph(self, node, entering):
        if node.parent.t == 'item':
            pass
        else:
            self.cr()

    def link(self, node, entering):
        if entering:
            self.out('`')
        else:
            self.out(' <%s>`_' % node.destination)

    def image(self, node, entering):
        directive = '.. image:: ' + node.destination

        if entering:
            self.out(directive)
            self.cr()
            self.indent_length += 4
            self.out(':alt: ')
        else:
            self.indent_length -= 4

    def code(self, node, entering):
        self.out('``')
        self.out(node.literal)
        self.out('``')

    def code_block(self, node, entering):
        directive = '.. code::'
        language_name = None

        info_words = node.info.split() if node.info else []
        if len(info_words) > 0 and len(info_words[0]) > 0:
            language_name = info_words[0]

        if language_name:
            directive += ' ' + language_name

        self.cr()
        self.out(directive)
        self.cr()
        self.cr()
        self.out(self.indent_lines(node.literal))
        self.cr()

    def list(self, node, entering):
        if entering:
            self.cr()

    def item(self, node, entering):
        tagname = '* ' if node.list_data['type'] == 'bullet' else '#. '

        if entering:
            self.out(tagname)
            self.indent_length += len(tagname)
        else:
            self.indent_length -= len(tagname)
            self.cr()

    def block_quote(self, node, entering):
        if entering:
            self.indent_length += 4
        else:
            self.indent_length -= 4

    def heading(self, node, entering):
        heading_chars = [
            '#',
            '*',
            '=',
            '-',
            '^',
            '"'
        ]

        try:
            heading_char = heading_chars[node.level-1]
        except IndexError:
            # Default to the last level if we're in too deep
            heading_char = heading_chars[-1]

        heading_length = len(node.first_child.literal)
        banner = heading_char * heading_length

        if entering:
            self.cr()
        else:
            self.cr()
            self.out(banner)
            self.cr()
