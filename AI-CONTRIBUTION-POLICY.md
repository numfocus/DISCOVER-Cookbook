# AI Contribution Policy for DISCOVER-Cookbook

**Version:** 1.0  
**Effective Date:** [To be determined by maintainers]  
**Last Updated:** [Date]  
**Authority:** NumFOCUS DISC Committee and DISCOVER-Cookbook Maintainers

## Overview

The NumFOCUS DISCOVER-Cookbook is a trusted resource for organizing diverse and inclusive events and conferences. This policy establishes clear guidelines for contributions that involve or utilize artificial intelligence (AI) and generative AI tools while maintaining the high quality, accuracy, and trustworthiness that our community expects.

## Scope

This policy applies to all contributions to the DISCOVER-Cookbook project, including:
- Content additions and modifications
- Documentation updates
- Code changes (build systems, CI/CD, etc.)
- Design elements and graphics
- Translation work
- Community discussions and proposals

## Policy Options

The maintainers present three policy approaches for community consideration:

### Option A: Guided AI Assistance (Recommended)

This balanced approach allows AI assistance while maintaining strict quality controls.

**Permitted AI Uses:**
- Grammar and style checking
- Language translation assistance
- Brainstorming and ideation support
- Research assistance for gathering information
- Template generation for consistent formatting
- Accessibility improvements suggestions

**Required Practices:**
1. **Transparency:** Contributors must disclose any use of AI tools in their contributions
2. **Human Oversight:** All AI-generated or AI-assisted content must be thoroughly reviewed, fact-checked, and validated by the human contributor
3. **Attribution:** Include a note in commit messages: `AI-assisted: [tool name] used for [specific purpose]`
4. **Quality Assurance:** Contributors are fully responsible for the accuracy, appropriateness, and quality of all submitted content

**Prohibited Uses:**
- Wholesale generation of content without substantial human review and modification
- Direct copying of AI-generated text without verification of facts and sources
- Use of AI for sensitive topics without expert review
- AI generation of legal or medical advice

### Option B: AI-Enhanced with Restrictions

This approach allows broader AI use with specific safeguards.

**Additional Permissions beyond Option A:**
- AI-assisted content creation for non-sensitive sections
- AI help with formatting and structuring documentation
- AI assistance in creating examples and case studies (with verification)

**Additional Requirements:**
- All AI-assisted content must be reviewed by at least one maintainer
- Contributors must provide sources for all factual claims in AI-assisted content
- AI-generated examples must be validated against real-world practices

### Option C: Minimal AI Use

This conservative approach restricts AI to basic tools.

**Permitted AI Uses:**
- Spell checking and grammar correction
- Basic translation assistance
- Accessibility checking tools

**Prohibited Uses:**
- Content generation or substantial writing assistance
- Research assistance beyond basic fact-checking
- Creative or strategic input from AI tools

## Implementation Guidelines

### For Contributors

1. **Before Contributing:**
   - Review this policy and understand which AI uses are permitted
   - Familiarize yourself with disclosure requirements
   - Ensure you have human expertise in the topic area

2. **During Development:**
   - Keep detailed records of any AI tool usage
   - Fact-check all AI-suggested information against authoritative sources
   - Apply critical thinking to all AI outputs

3. **When Submitting:**
   - Include AI usage disclosure in commit messages and PR descriptions
   - Provide sources for factual claims, especially in AI-assisted content
   - Be prepared to explain and defend the content during review

### For Reviewers

1. **AI-Assisted Content Review:**
   - Pay extra attention to factual accuracy
   - Verify that sources are properly cited
   - Check for consistent voice and style with project standards
   - Ensure sensitive topics are handled appropriately

2. **Red Flags:**
   - Generic or boilerplate language
   - Factual inconsistencies
   - Missing or inappropriate sourcing
   - Content that doesn't align with project values

## Quality Assurance

### Content Standards
All contributions, regardless of AI involvement, must meet these standards:
- **Accuracy:** All factual claims must be verifiable and current
- **Cultural Sensitivity:** Content must be inclusive and culturally appropriate
- **Practical Relevance:** Advice must be actionable and relevant to conference organizers
- **Source Attribution:** Proper citation of sources and references

### Review Process
1. **Initial Review:** Maintainers check for compliance with this policy
2. **Content Review:** Editors evaluate accuracy and relevance
3. **Community Feedback:** Open for community input during PR process
4. **Final Approval:** At least one maintainer approval required

## Enforcement

### Violations
Contributors who violate this policy may face:
- Request for revision and resubmission
- Temporary restriction from contributing
- Permanent ban for repeated or severe violations

### Appeals
Contributors may appeal enforcement decisions through:
1. Discussion with the maintainer who made the decision
2. Escalation to the full maintainer team
3. Final appeal to the NumFOCUS DISC Committee

## Legal and Ethical Considerations

### Copyright and Licensing
- Contributors are responsible for ensuring AI-generated content doesn't infringe copyright
- All contributions must be compatible with the project's MIT license
- Use of AI tools must comply with their terms of service

### Ethical Guidelines
- Respect the original creators of any content used to train AI models
- Consider the environmental impact of AI tool usage
- Maintain transparency with the community about AI involvement
- Prioritize human expertise, especially for sensitive D&I topics

## AI Tool Guidelines

### Acceptable Tools
Tools that provide transparency about their training data and license compatibility:
- Grammar checkers (Grammarly, LanguageTool)
- Translation services with clear usage rights
- Accessibility checking tools

### Use with Caution
- Large language models (ChatGPT, Claude, Gemini) - require extra verification
- Code generation tools - must validate against project standards
- Image generators - check licensing and cultural appropriateness

### Prohibited Tools
- Tools with unclear licensing terms for generated content
- Tools known to have been trained on unlicensed copyrighted material without permission
- Tools that restrict how generated content can be used in open source projects

## Resources and Support

### For Contributors
- [Contributing Guidelines](CONTRIBUTING.md)
- [Project Governance](GOVERNANCE.md)
- NumFOCUS Code of Conduct

### Getting Help
- Open a discussion thread for policy clarification
- Contact maintainers for guidance on specific AI tools
- Reach out to the NumFOCUS DISC Committee for appeals

## Policy Updates

This policy will be reviewed and updated as:
- AI technology evolves
- Legal frameworks develop
- Community needs change
- Best practices emerge

Updates require approval from:
1. Majority of active maintainers
2. Input from the editorial team
3. Final approval from NumFOCUS DISC Committee

## Appendix: Disclosure Templates

### Commit Message Template
```
Subject: Brief description of changes

Body: Detailed description of changes

AI-assisted: [Tool name] used for [specific purpose]
Human verification: [Brief note on validation performed]
Sources: [List any sources consulted]
```

### Pull Request Template Addition
```markdown
## AI Assistance Declaration
- [ ] This contribution does not use AI tools
- [ ] This contribution uses AI tools as disclosed below:
  - Tool(s) used: 
  - Purpose: 
  - Verification performed: 
  - Sources consulted: 
```

---

**Questions or Feedback?**
Please open a discussion thread or issue to discuss this policy or suggest improvements. 