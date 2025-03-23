# DISCOVER Cookbook Contribution Guide

NumFOCUS invites the community to make suggestions for improvements to the DISCOVER Cookbook. This guide outlines how to effectively contribute to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Types of Contributions](#types-of-contributions)
  - [Ideas, Questions, and Discussions](#ideas-questions-and-discussions)
  - [Problems or Issues](#problems-or-issues)
  - [Content and Design](#content-and-design)
  - [Bug Fixes](#bug-fixes)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Commit Messages](#commit-messages)
- [Review Process](#review-process)
- [Recognition](#recognition)

## Code of Conduct

All contributions should conform to the [NumFOCUS Contributor Code of Conduct](https://numfocus.org/code-of-conduct).

## Types of Contributions

The original body of work took place at a series of unconferences and various spurts of energy, today the DISCOVER-Cookbook is a living project with numerous contributors. Because it is code to produce a book rather than code for a software library or application, it has different needs than typical open source software systems. Because of these unique needs, we separate various types of contributions:

### Ideas, Questions, and Discussions

- For content suggestions, feature ideas, or general discussions, please use the [Discussions tab](https://github.com/numfocus/DISCOVER-Cookbook/discussions).
- Before submitting major content changes, we encourage starting a discussion to align with the project’s goals.

### Problems or Issues

- Submit issues on the [GitHub issue tracker](https://github.com/numfocus/DISCOVER-Cookbook/issues) with clear, detailed descriptions.
- Include steps to reproduce (for bugs) or context (for enhancements).
- Use appropriate labels/tags to categorize the issue.
- Check if a similar issue already exists before creating a new one.

### Content and Design

While content is the heart of the project, the quality of the content needs to remain high. Due to a high volume of generated text being submitted for review, content takes longer to review and approve. We value these contributions but understand that thorough review is necessary.

- Start with an idea in [discussions](https://github.com/numfocus/DISCOVER-Cookbook/discussions).
- Once the community approves, create an [issue](https://github.com/numfocus/DISCOVER-Cookbook/issues).
- Only then submit a PR referencing the approved issue.


### Bug Fixes

For technical issues with the book:

- **Check for existing issues** in our [issue tracker](https://github.com/numfocus/DISCOVER-Cookbook/issues).
- **Create a new issue** if none exists, with clear reproduction steps.
- **Reference the issue** in your pull request.
- **Test your changes locally** following our [build instructions](README.md) before submitting.

## Pull Request Guidelines

When submitting pull requests:

- Reference related issues (`Fixes #123` or `Related to #123`).
- Ensure you've built and tested the book locally.
- Your PR description clearly explains the changes.  
- You are open to feedback and respond to review comments.

## Commit Messages

Write clear, concise, and descriptive commit messages following this format:

**Format:**  
```
<Brief summary of changes (Aim for 50 characters max)>

<More detailed explanation if needed>

[Reference relevant issues, e.g., Fixes #123] 
```

**Examples:**
```
Fix typo in introduction section

Corrects a minor spelling mistake in the introduction 
of the documentation.

Fixes #42
```
**For more guidance, check out** [How to Write a Git Commit](https://cbea.ms/git-commit/).  
## Review Process

- **Technical fixes** generally receive faster review.
- **Content additions** undergo more thorough review by subject matter experts.
- **Revisions** may be requested before merging.
- **Final approval** comes from designated maintainers.

## Recognition

This project follows the [all-contributors specification](https://allcontributors.org/). Contributors are recognized in the Contributors section of the [README.md](README.md) file with emoji indicating their contribution types:

- 📖 Documentation
- 💻 Code
- 🤔 Ideas, Planning & Feedback
- 👀 Reviewed Pull Requests
- 🚧 Maintenance
- 💬 Answering Questions
- 🖋 Content

We value all forms of contributions and are grateful for your help in making events more diverse and inclusive.

---

Thank you for contributing to the DISCOVER Cookbook! Your efforts help create more welcoming and inclusive spaces in the scientific computing community.
