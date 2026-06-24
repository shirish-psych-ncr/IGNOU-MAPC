#!/usr/bin/env python3

with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add hero-title class to h1
content = content.replace(
    '<h1 class="text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight drop-shadow-lg">',
    '<h1 class="hero-title text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight drop-shadow-lg">'
)

# Add responsive classes to stats grid
content = content.replace(
    '<div class="mt-16 grid grid-cols-3 gap-4 max-w-lg mx-auto">',
    '<div class="mt-16 grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-lg mx-auto">'
)

# Update section headers to be responsive
content = content.replace(
    '<h2 class="text-4xl font-extrabold text-white">Core Psychology</h2>',
    '<h2 class="text-3xl sm:text-4xl font-extrabold text-white">Core Psychology</h2>'
)
content = content.replace(
    '<h2 class="text-4xl font-extrabold text-white">Practical &amp; Lab Components</h2>',
    '<h2 class="text-3xl sm:text-4xl font-extrabold text-white">Practical &amp; Lab Components</h2>'
)

# Update nav container padding
content = content.replace(
    '<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">',
    '<div class="nav-container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">'
)

# Update header section for mobile
content = content.replace(
    '<header class="relative min-h-screen flex items-center justify-center px-4 text-center pt-16">',
    '<header class="hero-section relative min-h-screen flex items-center justify-center px-4 text-center pt-16">'
)

with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added responsive classes!")
