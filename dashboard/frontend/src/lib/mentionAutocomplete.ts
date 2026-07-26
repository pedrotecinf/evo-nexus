export interface MentionAgent {
  name: string
  description: string
  locked: boolean
}

export interface MentionContext {
  start: number
  end: number
  query: string
}

export function findMentionContext(value: string, caret: number): MentionContext | null {
  const before = value.slice(0, caret)
  const match = before.match(/(^|\s)@([\w-]*)$/)
  if (!match) return null

  const query = match[2]
  return {
    start: caret - query.length - 1,
    end: caret,
    query,
  }
}

export function filterMentionAgents(
  agents: MentionAgent[],
  query: string,
  assignee: string | null,
): MentionAgent[] {
  const normalizedQuery = query.toLowerCase()
  return agents
    .filter(agent => !agent.locked)
    .filter(agent => !normalizedQuery || agent.name.toLowerCase().includes(normalizedQuery)
      || agent.description.toLowerCase().includes(normalizedQuery))
    .sort((a, b) => {
      const aIsAssignee = a.name === assignee
      const bIsAssignee = b.name === assignee
      if (aIsAssignee !== bIsAssignee) return aIsAssignee ? -1 : 1
      return a.name.localeCompare(b.name)
    })
}

export function insertMention(
  value: string,
  context: MentionContext,
  agentName: string,
): { value: string; caret: number } {
  const before = value.slice(0, context.start)
  const after = value.slice(context.end)
  const mention = `@${agentName}`
  const suffix = after && !/^[\s.,!?;:)]/.test(after) ? ' ' : ''
  const nextValue = `${before}${mention}${suffix}${after}`

  return { value: nextValue, caret: (before + mention + suffix).length }
}
