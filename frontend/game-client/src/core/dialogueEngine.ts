/**
 * Phase 4: Dialogue Engine
 *
 * 纯函数:接收 Dialogue + 当前节点 id + choice id → 返回下一节点。
 *
 * 规则:
 * - start(dialogue) → 返回 startNodeId 对应节点
 * - choose(dialogue, currentNodeId, choiceId) → 返回 choice.nextNodeId 对应节点
 * - 终止节点(terminal === true) → engine.isTerminal(node) 返回 true
 * - 节点 result 字段(success/failure/neutral)用于 quest 完成判定
 * - 跨节点引用 nextNodeId 必须能在 nodes 里找到,否则抛 DialogueReferenceError
 */

import type { Dialogue, DialogueNode } from '../schemas/content'

export class DialogueReferenceError extends Error {
  constructor(dialogueId: string, missingNodeId: string) {
    super(
      `Dialogue ${JSON.stringify(dialogueId)} 引用不存在的节点 ${JSON.stringify(missingNodeId)}`,
    )
    this.name = 'DialogueReferenceError'
  }
}

export function getStartNode(dialogue: Dialogue): DialogueNode {
  const node = dialogue.nodes.find((n) => n.id === dialogue.startNodeId)
  if (!node) {
    throw new DialogueReferenceError(dialogue.id, dialogue.startNodeId)
  }
  return node
}

export function chooseNode(
  dialogue: Dialogue,
  currentNode: DialogueNode,
  choiceId: string,
): DialogueNode | null {
  const choice = currentNode.choices.find((c) => c.id === choiceId)
  if (!choice) {
    // 选择 id 不存在,默认结束
    return null
  }
  // nextNodeId 为 null/undefined → 终止对话
  if (choice.nextNodeId == null) {
    return null
  }
  const nextNode = dialogue.nodes.find((n) => n.id === choice.nextNodeId)
  if (!nextNode) {
    throw new DialogueReferenceError(dialogue.id, choice.nextNodeId)
  }
  return nextNode
}

export function isTerminal(node: DialogueNode): boolean {
  return node.terminal === true || node.choices.length === 0
}

/**
 * 把 dialogue 里所有"成功 result"节点收集起来,用于判定 quest 完成条件。
 * 简单实现:Phase 4 quest 完成条件 = dialogue 至少有一个 success 节点被走到。
 * 复杂实现交给 Phase 4.1。
 */
export function reachedSuccessNode(
  dialogue: Dialogue,
  visitedNodeIds: Set<string>,
): boolean {
  return dialogue.nodes
    .filter((n) => n.result === 'success')
    .some((n) => visitedNodeIds.has(n.id))
}