#!/bin/bash

# Function to add an alias
add_alias() {
    local alias_name="$1"
    local alias_command="$2"
    local bashrc_file="$HOME/.bashrc"

    # Check if the alias already exists
    if grep -q "alias $alias_name=" "$bashrc_file"; then
        echo "Alias '$alias_name' already exists in $bashrc_file."
    else
        # Add the alias to .bashrc
        echo "alias $alias_name='$alias_command'" >> "$bashrc_file"
        echo "Alias '$alias_name' added to $bashrc_file."
    fi
}

# Example usage
# Replace 'll' and 'ls -la' with your desired alias name and command
add_alias "ll" "ls -la"

# Reload .bashrc to apply changes
source "$HOME/.bashrc"