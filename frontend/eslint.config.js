export default [
    {
        files: ['src/**/*.{js,jsx}'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            parserOptions: { ecmaFeatures: { jsx: true } },
            globals: {
                Blob: 'readonly',
                Event: 'readonly',
                TextEncoder: 'readonly',
                document: 'readonly',
                localStorage: 'readonly',
                window: 'readonly'
            }
        },
        rules: {
            'no-undef': 'error',
            'no-unused-vars': ['error', {
                argsIgnorePattern: '^_',
                varsIgnorePattern: '^React$'
            }]
        }
    }
]
