# Formatting

## `` trueconf.utils.formatting ⚓︎

### `` AllMention ⚓︎

Represents an `@all` mention.

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders an `@all` mention.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered `@all` mention. |

### `` Bold ⚓︎

```
Bold(*body)
```

Represents bold text.

Initializes a text container.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Plain strings or formatting nodes. | `()` |

#### `` body `instance-attribute` ⚓︎

```
body = body
```

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders the nested content as bold text.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered bold text. |

### `` Italic ⚓︎

```
Italic(*body)
```

Represents italic text.

Initializes a text container.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Plain strings or formatting nodes. | `()` |

#### `` body `instance-attribute` ⚓︎

```
body = body
```

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders the nested content as italic text.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered italic text. |

### `` LineBreak ⚓︎

Represents a line break.

Rendered as `
` in HTML and as `\n` in Markdown, since raw newlines are collapsed to spaces in HTML messages.

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders a line break.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered line break. |

### `` Link ⚓︎

```
Link(*body, url)
```

Represents a hyperlink.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Link label as plain text or formatting nodes. | `()` |
| `url` | `str` | Link target URL. | required |

Initializes a hyperlink node.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Link label as plain text or formatting nodes. | `()` |
| `url` | `str` | Link target URL. | required |

#### `` body `instance-attribute` ⚓︎

```
body = body
```

#### `` url `instance-attribute` ⚓︎

```
url = url
```

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders the nested content as a hyperlink.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered hyperlink. |

### `` Mention ⚓︎

```
Mention(*body, user_id)
```

Represents a TrueConf user mention.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Mention label as plain text or formatting nodes. | `()` |
| `user_id` | `str` | TrueConf user ID, for example `john_doe@video.example.com`. | required |

Initializes a TrueConf mention node.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Mention label as plain text or formatting nodes. | `()` |
| `user_id` | `str` | TrueConf user ID. | required |

#### `` body `instance-attribute` ⚓︎

```
body = body
```

#### `` user_id `instance-attribute` ⚓︎

```
user_id = user_id
```

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders the nested content as a TrueConf user mention.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered mention. |

### `` Strikethrough ⚓︎

```
Strikethrough(*body)
```

Represents strikethrough text.

Initializes a text container.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Plain strings or formatting nodes. | `()` |

#### `` body `instance-attribute` ⚓︎

```
body = body
```

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders the nested content as strikethrough text.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered strikethrough text. |

### `` Text ⚓︎

```
Text(*body)
```

Container node for plain text and nested formatting nodes.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Plain strings or formatting nodes to concatenate. | `()` |

### Example

```
content = Text("Hello, ", Bold("world"))
html = content.as_html()
```

Initializes a text container.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Plain strings or formatting nodes. | `()` |

#### `` body `instance-attribute` ⚓︎

```
body = body
```

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders the text container using the provided decoration strategy.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered text. |

### `` Underline ⚓︎

```
Underline(*body)
```

Represents underlined text.

Initializes a text container.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*body` | `str | TextNode` | Plain strings or formatting nodes. | `()` |

#### `` body `instance-attribute` ⚓︎

```
body = body
```

#### `` as_html ⚓︎

```
as_html()
```

Renders the node as HTML.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | HTML representation of the formatted text. |

#### `` as_markdown ⚓︎

```
as_markdown()
```

Renders the node as Markdown.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Markdown representation of the formatted text. |

#### `` render ⚓︎

```
render(decoration)
```

Renders the nested content as underlined text.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `decoration` | `TextDecoration` | Formatting strategy used for rendering. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Rendered underlined text. |

June 30, 2026

May 5, 2026
