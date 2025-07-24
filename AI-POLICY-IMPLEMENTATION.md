# AI Policy Implementation Checklist

## Pre-Implementation

### Decision Making
- [ ] Review the three policy options (A, B, C) in [AI-CONTRIBUTION-POLICY.md](AI-CONTRIBUTION-POLICY.md)
- [ ] Gather input from maintainers and editorial team
- [ ] Hold community discussion (GitHub Discussions recommended)
- [ ] Get approval from NumFOCUS DISC Committee
- [ ] Document final decision and effective date

### Communication
- [ ] Announce policy development in project communications
- [ ] Share draft policy for community feedback
- [ ] Allow adequate time for review and input (suggest 2-4 weeks)
- [ ] Address community concerns and questions

## Implementation Steps

### 1. Documentation Updates
- [ ] Finalize AI-CONTRIBUTION-POLICY.md with chosen option
- [ ] Update CONTRIBUTING.md (already done)
- [ ] Add policy reference to README.md if appropriate
- [ ] Update any contributor onboarding materials

### 2. Process Updates
- [ ] Create/update pull request template with AI disclosure section
- [ ] Update issue templates if needed
- [ ] Train maintainers and editors on new review process
- [ ] Document enforcement procedures

### 3. Tool Integration
- [ ] Add AI policy check to PR review checklist
- [ ] Consider GitHub Actions or other automation for policy reminders
- [ ] Update any contributor tools or scripts

### 4. Community Communication
- [ ] Publish final policy announcement
- [ ] Update project website/documentation site
- [ ] Inform regular contributors about new requirements
- [ ] Create FAQ section for common questions

## Post-Implementation

### Monitoring and Adjustment
- [ ] Track policy compliance in first month
- [ ] Gather feedback from contributors and reviewers
- [ ] Document any issues or ambiguities
- [ ] Schedule 3-month policy review

### Review Process Updates
- [ ] Train new reviewers on AI content evaluation
- [ ] Develop review guidelines for AI-assisted content
- [ ] Create escalation process for policy questions
- [ ] Monitor review time impact

### Community Support
- [ ] Create discussion space for policy questions
- [ ] Provide examples of compliant AI usage
- [ ] Address contributor concerns promptly
- [ ] Maintain policy documentation

## Pull Request Template Update

Add this section to `.github/pull_request_template.md`:

```markdown
## AI Assistance Declaration
Please check one:
- [ ] This contribution does not use AI tools
- [ ] This contribution uses AI tools as disclosed below:

If you used AI tools, please provide:
- **Tool(s) used:** 
- **Purpose:** (e.g., grammar checking, research assistance, translation)
- **Verification performed:** (e.g., fact-checked sources, reviewed for accuracy)
- **Sources consulted:** (list any sources used to verify AI output)

By submitting this PR, I confirm that any AI-assisted content has been thoroughly reviewed and I take full responsibility for its accuracy and quality.
```

## Review Guidelines for Maintainers

### For AI-Assisted Content
1. **Verify Disclosure:** Ensure AI usage is properly disclosed
2. **Check Sources:** Verify any factual claims have proper attribution
3. **Quality Review:** Extra attention to accuracy and consistency
4. **Cultural Sensitivity:** Ensure D&I content maintains appropriate sensitivity
5. **Project Alignment:** Confirm content aligns with project goals and voice

### Red Flags
- Generic or template-like language without customization
- Factual errors or outdated information
- Missing sources for specific claims
- Content that doesn't match project style/voice
- Undisclosed AI usage (if suspected)

## Timeline Recommendations

### Week 1-2: Decision and Planning
- Review options and make policy decision
- Plan implementation approach
- Prepare communication materials

### Week 3-4: Community Input
- Share draft policy for feedback
- Address questions and concerns
- Refine policy based on input

### Week 5-6: Implementation
- Update documentation and processes
- Train team members
- Deploy new procedures

### Week 7+: Monitoring
- Monitor compliance and effectiveness
- Gather feedback and iterate
- Schedule regular policy reviews

## Success Metrics

### Short-term (1-3 months)
- [ ] Policy compliance rate >90%
- [ ] Clear disclosure in AI-assisted contributions
- [ ] No major quality issues with AI-assisted content
- [ ] Community acceptance and understanding

### Long-term (6+ months)
- [ ] Maintained content quality standards
- [ ] Positive contributor experience
- [ ] No legal or licensing issues
- [ ] Policy adaptations based on experience

## Common Questions and Answers

**Q: What if I'm not sure if a tool counts as AI?**
A: When in doubt, disclose it. It's better to over-disclose than under-disclose.

**Q: Do I need to disclose spell-check or grammar tools?**
A: Basic spell-check tools (like built-in browser spell-check) don't need disclosure. Advanced AI grammar tools (like Grammarly) should be disclosed.

**Q: What if I used AI for brainstorming but rewrote everything myself?**
A: Disclose the brainstorming assistance but note that content was independently created.

**Q: Can I use AI for translation work?**
A: Yes, with disclosure and human verification of accuracy and cultural appropriateness.

## Contact Information

For questions about policy implementation:
- Open a GitHub Discussion
- Contact project maintainers
- Escalate to NumFOCUS DISC Committee if needed

---

**Note:** This implementation guide should be customized based on the specific needs and decision of the DISCOVER-Cookbook project team. 