# Florence-2 MCP Server
An MCP server for processing images using Florence-2.

## Installation

### For Claude Desktop
To configure this server for Claude Desktop, edit the `claude_desktop_config.json` file with the following entry under
`mcpServers`:

```json
{
  "mcpServers": {
    "florence-2": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jkawamoto/mcp-florence2",
        "mcp-florence2"
      ]
    }
  }
}
```
After editing, restart the application.
For more information,
see: [For Claude Desktop Users - Model Context Protocol](https://modelcontextprotocol.io/quickstart/user).

### For Goose CLI
To enable the Bear extension in Goose CLI,
edit the configuration file `~/.config/goose/config.yaml` to include the following entry:

```yaml
extensions:
  bear:
    name: Florence-2
    cmd: uvx
    args: [--from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2]
    enabled: true
    type: stdio
```

### For Goose Desktop
Add a new extension with the following settings:

- **Type**: Standard IO
- **ID**: florence-2
- **Name**: Florence-2
- **Description**: An MCP server for processing images using Florence-2
- **Command**: `uvx --from git+https://github.com/jkawamoto/mcp-florence2 mcp-florence2`

For more details on configuring MCP servers in Goose Desktop,
refer to the documentation:
[Using Extensions - MCP Servers](https://block.github.io/goose/docs/getting-started/using-extensions#mcp-servers).


## License
This application is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.