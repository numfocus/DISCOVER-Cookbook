## Title
Translation Project for DISCOVER-Cookbook

## Abstract
The NumFOCUS DISCOVER-Cookbook (Diverse & Inclusive Spaces and Conferences: Overall Vision and Essential Resources) is a guide for organizing more diverse and inclusive events and conferences. Translating the content will make it accessible to a broader audience, fostering a global community of users. The project involves generating translations for the DISCOVER-cookbook, integrating language selection switches, updating translations as content changes, and engaging translators to contribute.

## Technical Details

### 1. Generating Translations
**What We Are Doing:** Translating the entire content of the DISCOVER-cookbook into multiple languages.

**Technical Approach:**
-  Working with translation communities that could provide the translation and feedback, e.g. [translatewiki](https://translatewiki.net/).

- Machine Translation APIs: [Google Cloud Translation API](https://cloud.google.com/translate), [Microsoft Translator Text API](https://azure.microsoft.com/en-us/services/cognitive-services/translator/).
- Establish a workflow for translating existing content, ensuring consistency and accuracy.

**Translation Workflow:**
- Source content is pushed to a repository.
- Automatic translation requests are sent to Machine Translation APIs.
- Translations are reviewed and edited by human translators using a Translation Management System.
- Translations are merged back into the repository.

### 2. Adding Language Switches
**What We Are Doing:** Integrating switches within the book to allow users to select their preferred language.

**Technical Approach:**
- Identify and implement language switch mechanisms (e.g., dropdown menus, toggle buttons) within the book's platform.
- YAML-based translation and Jinja2 templates are flexible for multilingual content.
- Test the functionality across different devices and browsers to ensure seamless language switching.

### 3. Updating Translations
**What We Are Doing:** Developing a system to update translations as the book's content changes.

**Technical Approach:**
- Create a process for tracking changes in the original content.
- Version Control Systems: Git with GitHub Actions, Crowdin.
- Implement a notification system to inform translators of updates.

### 4. Engaging Translators
**What We Are Doing:** Calling for translators to sign up and get tagged for their contributions.

**Technical Approach:**
- Announce a call for translators on relevant platforms (e.g., social media, forums, community websites).
- Web Forms and Authentication: Using [Google Forms](https://www.google.com/forms/about/) or [Typeform](https://www.typeform.com/) for sign-ups, along with authentication tools like [Auth0](https://auth0.com/).
- Develop a tagging system to acknowledge and credit translators for their contributions.
- Provide resources and support for translators to ensure high-quality translations (e.g., guidelines, glossaries, support forums).

## Schedule of Deliverables
**Community Bonding Period**
- Get to know the community better.
- Ensure build environment is set up.
- Discuss project in detail with the community.

**Phase 1**
- Initial translation of existing content.

**Phase 2**
- Integration of language switches.

**Phase 3**
- System for updating translations.

**Phase 4**
- Engagement and onboarding of translators.

**Final Week**
- Finish up the project.

## Development Experience
**Contributions on DISCOVER-Cookbook ([DISCOVER-Cookbook](https://github.com/numfocus/DISCOVER-Cookbook)):**
- Adds Infectious Disease Precautions to health protocols [PR 181](https://github.com/numfocus/DISCOVER-Cookbook/pull/181)
- Adding a QA guide to improve asking questions inclusively [PR 180](https://github.com/numfocus/DISCOVER-Cookbook/pull/180)
- Updated the document to enhance accessibility for attendees with disabilities at conferences. [PR 171](https://github.com/numfocus/DISCOVER-Cookbook/pull/171)
- Added a printable DISCOVER-Cookbook checklist for the organizers [PR 166](https://github.com/numfocus/DISCOVER-Cookbook/pull/166)

**Contributions on other NumFOCUS projects:**
- Updated geovisualization, README.md, installation.rst. Added legendgram to geovisualization, updated README.md with graph module and added installation for graph in --installation.rst [PR 1361](https://github.com/pysal/pysal/pull/1361)
- Added the missing dependency ([https://github.com/pysal/momepy/pull/681](https://github.com/pysal/momepy/pull/681))
- Added ruff and pre-commit in the contributing file ([https://github.com/pysal/momepy/pull/683](https://github.com/pysal/momepy/pull/683))
- Updated the formulations in the docs ([https://github.com/pysal/spopt/pull/468](https://github.com/pysal/spopt/pull/468))

**Contributions to Bambi ([bambi](https://github.com/bambinos/bambi)):**
- Addresses #644 Questions for FAQ [PR 881](https://github.com/bambinos/bambi/pull/881)
- Adding piecewise regression examples in example docs [PR](https://github.com/bambinos/bambi/pull/884)
- Created truncatedprior.py [PR 885](https://github.com/bambinos/bambi/pull/885)

**Contributions to other projects:**
- Added feedback template [PR 1](https://github.com/speco29/advisory-database/pull/1)
- Added contributing.md to the project [PR 7](https://github.com/numfocus/MOSS/pull/7)
- Correcting the title of English lecture, which was written in Spanish [PR 374](https://github.com/PyAr/PyZombis/pull/374)

**Other Experiences**
- Currently working on a hackathon project named PyPiePie [PyPiePie](https://github.com/AstroAirafar/PyPiePie): A game to teach Python via stories and projects.

## Why This Project?
The NumFOCUS DISCOVER Cookbook is a transformative initiative aimed at fostering diversity and inclusion in the scientific and computing communities. It fosters the following:
- Promoting Diversity and Inclusion.
- Empowering Communities.
- Long-Term Change: The project aims to create lasting change by embedding diversity and inclusion into the fabric of scientific conferences and events. This enduring impact benefits current and future generations of scientists and technologists.

## Why Do You Want to Do This Project?
I am deeply committed to promoting diversity and inclusion in all areas of life, including the scientific and computing communities. This project aligns perfectly with my values and aspirations. My background in software development, data analysis, and project planning makes me well-suited to contribute effectively to this project. I can apply my skills to create comprehensive and user-friendly resources. This project provides a unique opportunity to learn from experts in diversity and inclusion, expanding my knowledge and understanding of these crucial areas. Being part of the NumFOCUS DISCOVER Cookbook project means contributing to meaningful change that enhances the inclusivity and accessibility of scientific events. This impact resonates with my desire to make a positive difference in the world.
