#!/usr/bin/env node

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');

// Update the list of directories and files to ignore
const ignoredDirectories = [
    '.git',
    'docs/validation',
];

const ignoredFiles = [
    'documentation_generator.js',
    'dockerignore',
    '.env_secrets',
    '.env.backup',
    '.env.example',
];

// Add list of files to skip content but include in structure
const ignoreContentButIncludeInStructure = [
    'env_secrets',
    '.gitignore',
    '.env',
    'documentation_generator.js',
    'dockerignore',
    '.env_secrets',
    '.env.backup',
    '.env.example',
];

// Add a pattern to match generated documentation files
const generatedFilePattern = /^documentation_.*\.md$/;

class DocumentationGenerator {
    constructor() {
        this.projectRoot = this.findProjectRoot(process.cwd());
    }

    // Add new method to find project root (looks for package.json or .git)
    findProjectRoot(currentPath) {
        const markers = ['package.json', '.git'];
        const root = path.parse(currentPath).root;

        let current = currentPath;
        while (current !== root) {
            if (markers.some(marker => fsSync.existsSync(path.join(current, marker)))) {
                return current;
            }
            current = path.dirname(current);
        }
        return currentPath; // fallback to current directory if no project root found
    }

    async* walkDirectoryStructure(dir, level = 0) {
        const files = await fs.readdir(dir, { withFileTypes: true });
        const indent = '  '.repeat(level);
        
        // Sort entries - directories first, then files
        const sortedFiles = files.sort((a, b) => {
            if (a.isDirectory() && !b.isDirectory()) return -1;
            if (!a.isDirectory() && b.isDirectory()) return 1;
            return a.name.localeCompare(b.name);
        });

        for (const file of sortedFiles) {
            const res = path.resolve(dir, file.name);
            const relativePath = path.relative(this.projectRoot, res);
            const currentDirectoryName = path.basename(res);

            // Modify the directory traversal to skip ignored directories and files
            if (
                ignoredDirectories.includes(currentDirectoryName) ||
                relativePath.includes('docs/validation') ||
                (file.isFile() && (
                    ignoredFiles.includes(file.name) ||
                    generatedFilePattern.test(file.name)
                ))
            ) {
                continue;
            }
            
            if (file.isDirectory()) {
                yield `${indent}- ${relativePath}/`;
                yield* this.walkDirectoryStructure(res, level + 1);
            } else {
                yield `${indent}- ${relativePath}`;
            }
        }
    }

    async generateDocumentation() {
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '').split('T')[0];
            const date = new Date();
            const hour = date.getHours().toString().padStart(2, '0');
            const minutes = date.getMinutes().toString().padStart(2, '0');
            const outputFile = path.join(this.projectRoot, `documentation_${timestamp}_${hour}h${minutes}m.md`);
            
            let content = '# Project Structure\n\n';

            // Generate complete directory structure
            for await (const entry of this.walkDirectoryStructure(this.projectRoot)) {
                content += `${entry}\n`;
            }

            content += '\n# File Contents\n\n';

            // Add all file contents without categorization
            for await (const filePath of this.walkDirectoryStructure(this.projectRoot)) {
                if (!filePath.endsWith('/')) {  // Skip directories
                    const absolutePath = path.join(this.projectRoot, filePath.replace(/^[\s-]+/, ''));
                    const fileName = path.basename(absolutePath);

                    // Skip adding content for files in 'ignoreContentButIncludeInStructure'
                    if (ignoreContentButIncludeInStructure.includes(fileName)) {
                        // Include the file in the structure but skip its content
                        continue;
                    }

                    try {
                        const fileContent = await fs.readFile(absolutePath, 'utf8');
                        content += `## ${filePath.replace(/^[\s-]+/, '')}\n\n\`\`\`\n${fileContent}\n\`\`\`\n\n`;
                    } catch (err) {
                        // Skip binary files or files that can't be read
                        continue;
                    }
                }  // <-- Add this closing brace
            }

            await fs.writeFile(outputFile, content);
            console.log(`Documentation generated: ${outputFile}`);
        } catch (error) {
            console.error('Error generating documentation:', error);
        }
    }
}

new DocumentationGenerator().generateDocumentation();