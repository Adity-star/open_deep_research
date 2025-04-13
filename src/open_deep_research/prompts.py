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
