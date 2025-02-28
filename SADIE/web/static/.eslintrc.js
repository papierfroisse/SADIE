/**
 * Configuration ESLint pour le projet SADIE
 * 
 * Cette configuration est optimisée pour React avec TypeScript et inclut
 * des règles pour garantir la qualité du code et prévenir les erreurs courantes.
 */

module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
    project: './tsconfig.json',
    tsconfigRootDir: __dirname,
  },
  env: {
    browser: true,
    node: true,
    es6: true,
    jest: true,
  },
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      typescript: {},
      node: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
      },
    },
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:jsx-a11y/recommended',
    'plugin:import/errors',
    'plugin:import/warnings',
    'plugin:import/typescript',
    'plugin:prettier/recommended', // Doit être en dernier pour éviter les conflits
  ],
  plugins: [
    'react',
    'react-hooks',
    '@typescript-eslint',
    'jsx-a11y',
    'import',
    'prettier',
  ],
  rules: {
    // -- Règles générales
    'no-console': ['warn', { allow: ['warn', 'error', 'info'] }],
    'no-debugger': 'warn',
    'no-duplicate-imports': 'error',
    'no-unused-vars': 'off', // Remplacé par la règle TypeScript
    'prefer-const': 'error',
    'eqeqeq': ['error', 'always', { null: 'ignore' }],
    'spaced-comment': ['warn', 'always'],
    'sort-imports': ['warn', { ignoreDeclarationSort: true }],

    // -- Règles TypeScript
    '@typescript-eslint/no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    '@typescript-eslint/no-empty-function': ['warn', { 
      allow: ['arrowFunctions'] 
    }],
    '@typescript-eslint/ban-ts-comment': ['warn', {
      'ts-ignore': 'allow-with-description',
      minimumDescriptionLength: 10,
    }],
    '@typescript-eslint/no-floating-promises': 'error',
    '@typescript-eslint/no-misused-promises': [
      'error',
      {
        checksVoidReturn: false,
      },
    ],
    '@typescript-eslint/await-thenable': 'error',

    // -- Règles React
    'react/prop-types': 'off', // TypeScript gère déjà la validation des props
    'react/react-in-jsx-scope': 'off', // Non nécessaire avec les nouvelles versions de React
    'react/display-name': 'off',
    'react/no-unescaped-entities': 'off',
    'react/jsx-curly-brace-presence': ['warn', { props: 'never', children: 'never' }],
    'react/jsx-key': ['error', { checkFragmentShorthand: true }],
    'react/jsx-no-useless-fragment': 'warn',
    'react/jsx-pascal-case': 'error',
    'react/self-closing-comp': 'warn',

    // -- Règles des hooks React
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // -- Règles d'accessibilité
    'jsx-a11y/anchor-is-valid': ['warn', {
      components: ['Link'],
      specialLink: ['to', 'hrefLeft', 'hrefRight'],
      aspects: ['noHref', 'invalidHref', 'preferButton'],
    }],
    'jsx-a11y/media-has-caption': 'off',
    'jsx-a11y/no-autofocus': 'off',

    // -- Règles d'import
    'import/order': ['warn', {
      groups: [
        'builtin',
        'external',
        'internal',
        ['parent', 'sibling'],
        'index',
        'object',
        'type',
      ],
      'newlines-between': 'always',
      alphabetize: { order: 'asc', caseInsensitive: true },
    }],
    'import/no-unresolved': 'error',
    'import/no-cycle': 'warn',
    'import/no-unused-modules': 'warn',
    'import/no-duplicates': 'error',

    // -- Règles Prettier (pour éviter les conflits)
    'prettier/prettier': ['warn', {}, { usePrettierrc: true }],
  },
  overrides: [
    // Configuration spécifique pour les fichiers de test
    {
      files: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
      env: {
        jest: true,
      },
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-non-null-assertion': 'off',
        'import/no-extraneous-dependencies': ['off', { 
          devDependencies: true 
        }],
      },
    },
    // Configuration spécifique pour les fichiers de configuration
    {
      files: [
        '.eslintrc.js',
        'jest.config.js',
        'babel.config.js',
        'webpack.config.js',
        'vite.config.ts',
        'scripts/**/*.js',
      ],
      env: {
        node: true,
      },
      rules: {
        '@typescript-eslint/no-var-requires': 'off',
        '@typescript-eslint/no-explicit-any': 'off',
        'import/no-extraneous-dependencies': ['off', { 
          devDependencies: true 
        }],
      },
    },
  ],
  ignorePatterns: [
    'node_modules',
    'build',
    'dist',
    'coverage',
    '*.min.js',
    '*.d.ts',
    'public',
    'reports',
  ],
}; 