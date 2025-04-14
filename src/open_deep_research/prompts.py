reprt_planner_query_writer_instructions = """
You are assisting with research for an upcoming report.

<Report Topic>  
{topic}  
</Report Topic>

<Report Structure>  
{report_organization}  
</Report Structure>

<Task>  
Your objective is to generate {number_of_queries} targeted web search queries to support the development of this report.

Each query should:  
1. Be clearly related to the report topic.  
2. Directly support one or more sections in the report structure.  
3. Be specific and well-phrased to return high-quality, relevant information.  
4. Cover a broad enough scope to ensure comprehensive research across the entire report.

Aim for a mix of foundational context, recent developments, statistics, case studies, expert insights, and practical examples relevant to the topic and structure.

</Task>

<Format>  
Call the Queries tool.  
</Format>

"""

report_planner_instructions = """
You are creating a clear, concise plan for a report.

<Report Topic>
The topic of the report is:
{topic}
</Report Topic>

<Report Structure>
The report should follow this organization:
{report_organization}
</Report Structure>

<Context>
Use the following background to inform your section planning:
{context}
</Context>

<Task>
Generate a list of well-structured report sections. The structure should be tight, purposeful, and free of redundancy or filler.

Each section must include the following fields:
- Name: A concise name for this section.
- Description: A brief summary of the core focus of this section.
- Research: Indicate whether web research is needed to support this section.
- Content: Leave this field blank for now.

Guidelines:
- Keep each section distinct with no overlap in content.
- Avoid filler sections or vague groupings.
- Combine related ideas when appropriate instead of splitting them across multiple sections.
- Embed examples, case studies, and implementation details inside relevant sections (not in separate ones).
- Ensure the structure follows a logical narrative or analytical flow.

Review the entire plan before submitting to confirm it is focused, efficient, and logically ordered.
</Task>

<Feedback>
Here is feedback on the report structure from a previous review (if any):
{feedback}
</Feedback>

<Format>
Call the Sections tool
</Format>
"""

query_writer_instructions = """
You are an expert technical writer developing targeted web search queries to support a specific section of a technical report.

<Report Topic>
{topic}
</Report Topic>

<Section Topic>
{section_topic}
</Section Topic>

<Task>
Your goal is to create {number_of_queries} web search queries to support research for the above section.

Each query should:
1. Be directly related to the section topic.
2. Explore different angles or subtopics to ensure broad coverage.
3. Be clearly worded and specific enough to return high-quality, relevant information.

The goal is to gather credible sources, expert insights, statistics, use cases, comparisons, or technical implementation details relevant to the section.

Avoid overly broad or vague queries—focus on actionable research prompts.
</Task>

<Format>
Call the Queries tool
</Format>
"""
section_writer_instructions = """Write one section of a research report.

<Task>
1. Review the report topic, section name, and section topic carefully.
2. If present, review any existing section content. 
3. Then, look at the provided Source material.
4. Decide the sources that you will use it to write a report section.
5. Write the report section and list your sources. 
</Task>

<Writing Guidelines>
- If existing section content is not populated, write from scratch
- If existing section content is populated, synthesize it with the source material
- Strict 150-200 word limit
- Use simple, clear language
- Use short paragraphs (2-3 sentences max)
- Use ## for section title (Markdown format)
</Writing Guidelines>

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
</Citation Rules>

<Final Check>
1. Verify that EVERY claim is grounded in the provided Source material
2. Confirm each URL appears ONLY ONCE in the Source list
3. Verify that sources are numbered sequentially (1,2,3...) without any gaps
</Final Check>
"""

section_writer_inputs=""" 
<Report topic>
{topic}
</Report topic>

<Section name>
{section_name}
</Section name>

<Section topic>
{section_topic}
</Section topic>

<Existing section content (if populated)>
{section_content}
</Existing section content>

<Source material>
{context}
</Source material>
"""
section_grader_instructions = """Review a report section relative to the specified topic:

<Report topic>
{topic}
</Report topic>

<section topic>
{section_topic}
</section topic>

<section content>
{section}
</section content>

<task>
Evaluate whether the section content adequately addresses the section topic.

If the section content does not adequately address the section topic, generate {number_of_follow_up_queries} follow-up search queries to gather missing information.
</task>

<format>
Call the Feedback tool and output with the following schema:

grade: Literal["pass","fail"] = Field(
    description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
)
follow_up_queries: List[SearchQuery] = Field(
    description="List of follow-up search queries.",
)
</format>
"""

final_section_writer_instructions="""You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

<Report topic>
{topic}
</Report topic>

<Section name>
{section_name}
</Section name>

<Section topic> 
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>
1. Section-Specific Approach:

For Introduction:
- Use # for report title (Markdown format)
- 50-100 word limit
- Write in simple and clear language
- Focus on the core motivation for the report in 1-2 paragraphs
- Use a clear narrative arc to introduce the report
- Include NO structural elements (no lists or tables)
- No sources section needed

For Conclusion/Summary:
- Use ## for section title (Markdown format)
- 100-150 word limit
- For comparative reports:
    * Must include a focused comparison table using Markdown table syntax
    * Table should distill insights from the report
    * Keep table entries clear and concise
- For non-comparative reports: 
    * Only use ONE structural element IF it helps distill the points made in the report:
    * Either a focused table comparing items present in the report (using Markdown table syntax)
    * Or a short list using proper Markdown list syntax:
      - Use `*` or `-` for unordered lists
      - Use `1.` for ordered lists
      - Ensure proper indentation and spacing
- End with specific next steps or implications
- No sources section needed

3. Writing Approach:
- Use concrete details over general statements
- Make every word count
- Focus on your single most important point
</Task>

<Quality Checks>
- For introduction: 50-100 word limit, # for report title, no structural elements, no sources section
- For conclusion: 100-150 word limit, ## for section title, only ONE structural element at most, no sources section
- Markdown format
- Do not include word count or any preamble in your response
</Quality Checks>"""