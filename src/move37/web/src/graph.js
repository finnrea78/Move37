const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

function unique(values) {
  return [...new Set(values)];
}

export function fibonacciSphere(index, total) {
  if (total <= 1) {
    return { x: 0, y: 0, z: 1 };
  }
  const y = 1 - (index / (total - 1)) * 2;
  const radius = Math.sqrt(Math.max(0, 1 - y * y));
  const theta = GOLDEN_ANGLE * index;
  return {
    x: Math.cos(theta) * radius,
    y,
    z: Math.sin(theta) * radius,
  };
}

export function rotateY(point, angle) {
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return {
    x: point.x * cos + point.z * sin,
    y: point.y,
    z: -point.x * sin + point.z * cos,
  };
}

export function rotateX(point, angle) {
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return {
    x: point.x,
    y: point.y * cos - point.z * sin,
    z: point.y * sin + point.z * cos,
  };
}

export function formatHours(hours) {
  if (hours == null || Number.isNaN(hours)) {
    return "n/a";
  }
  return `${hours.toFixed(hours >= 10 ? 0 : 1)}h`;
}

export function createNodeId(title, nodes) {
  const base = String(title || "activity")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "") || "activity";
  let candidate = base;
  let index = 2;
  const ids = new Set(nodes.map((node) => node.id));
  while (ids.has(candidate)) {
    candidate = `${base}-${index}`;
    index += 1;
  }
  return candidate;
}

export function buildIndexes(nodes, dependencies) {
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const parentMap = new Map(nodes.map((node) => [node.id, []]));
  const childMap = new Map(nodes.map((node) => [node.id, []]));
  dependencies.forEach((edge) => {
    if (!nodeMap.has(edge.parentId) || !nodeMap.has(edge.childId)) {
      return;
    }
    parentMap.get(edge.childId).push(edge.parentId);
    childMap.get(edge.parentId).push(edge.childId);
  });
  return { nodeMap, parentMap, childMap };
}

export function topologicalSort(nodes, edges) {
  const adjacency = new Map(nodes.map((node) => [node.id, []]));
  const indegree = new Map(nodes.map((node) => [node.id, 0]));
  edges.forEach((edge) => {
    if (!adjacency.has(edge.parentId) || !adjacency.has(edge.childId)) {
      return;
    }
    adjacency.get(edge.parentId).push(edge.childId);
    indegree.set(edge.childId, indegree.get(edge.childId) + 1);
  });
  const queue = nodes
    .map((node) => node.id)
    .filter((id) => indegree.get(id) === 0);
  const ordered = [];
  while (queue.length) {
    const id = queue.shift();
    ordered.push(id);
    adjacency.get(id).forEach((childId) => {
      indegree.set(childId, indegree.get(childId) - 1);
      if (indegree.get(childId) === 0) {
        queue.push(childId);
      }
    });
  }
  return {
    ordered,
    hasCycle: ordered.length !== nodes.length,
  };
}

export function wouldCreateCycle(nodes, dependencies, nextEdge) {
  if (nextEdge.parentId === nextEdge.childId) {
    return true;
  }
  const { childMap } = buildIndexes(nodes, dependencies);
  const stack = [nextEdge.childId];
  const visited = new Set();
  while (stack.length) {
    const current = stack.pop();
    if (current === nextEdge.parentId) {
      return true;
    }
    if (visited.has(current)) {
      continue;
    }
    visited.add(current);
    (childMap.get(current) || []).forEach((childId) => stack.push(childId));
  }
  return false;
}

export function collectDescendants(id, childMap) {
  const result = new Set();
  const stack = [...(childMap.get(id) || [])];
  while (stack.length) {
    const current = stack.pop();
    if (result.has(current)) {
      continue;
    }
    result.add(current);
    (childMap.get(current) || []).forEach((childId) => stack.push(childId));
  }
  return result;
}

export function collectAncestors(id, parentMap) {
  const result = new Set();
  const stack = [...(parentMap.get(id) || [])];
  while (stack.length) {
    const current = stack.pop();
    if (result.has(current)) {
      continue;
    }
    result.add(current);
    (parentMap.get(current) || []).forEach((parentId) => stack.push(parentId));
  }
  return result;
}

export function computeBaseLevels(nodes, dependencies) {
  const { parentMap, childMap } = buildIndexes(nodes, dependencies);
  const { ordered, hasCycle } = topologicalSort(nodes, dependencies);
  if (hasCycle) {
    throw new Error("Dependency graph contains a cycle.");
  }
  const minimal = new Map(nodes.map((node) => [node.id, 0]));
  ordered.forEach((id) => {
    const parents = parentMap.get(id) || [];
    const next = parents.length
      ? Math.max(...parents.map((parentId) => minimal.get(parentId) + 1))
      : 0;
    minimal.set(id, next);
  });

  const globalMax = Math.max(...ordered.map((id) => minimal.get(id)), 0);
  const levels = new Map();
  const reverse = [...ordered].reverse();

  reverse.forEach((id) => {
    const parents = parentMap.get(id) || [];
    const children = childMap.get(id) || [];
    if (parents.length === 0 && children.length === 0) {
      levels.set(id, globalMax);
      return;
    }
    if (parents.length === 0) {
      levels.set(id, 0);
      return;
    }
    if (children.length === 0) {
      levels.set(id, globalMax);
      return;
    }
    const maxAllowed = Math.min(...children.map((childId) => levels.get(childId))) - 1;
    levels.set(id, Math.max(minimal.get(id), maxAllowed));
  });

  return { baseLevels: levels, globalBaseMax: globalMax, parentMap, childMap };
}

export function computeScheduleLayout(nodes, schedules, baseLevels) {
  const levels = unique([...baseLevels.values()]).sort((left, right) => left - right);
  const scheduledIds = new Set(
    nodes.filter((node) => String(node.startDate || "").trim()).map((node) => node.id),
  );

  levels.forEach((level) => {
    const levelNodeIds = nodes
      .filter((node) => baseLevels.get(node.id) === level)
      .map((node) => node.id);
    const levelSet = new Set(levelNodeIds);
    if (!levelNodeIds.length) {
      return;
    }
    const adjacency = new Map(levelNodeIds.map((id) => [id, []]));
    const indegree = new Map(levelNodeIds.map((id) => [id, 0]));

    schedules.forEach((rule) => {
      if (!levelSet.has(rule.earlierId) || !levelSet.has(rule.laterId)) {
        return;
      }
      adjacency.get(rule.laterId).push(rule.earlierId);
      indegree.set(rule.earlierId, indegree.get(rule.earlierId) + 1);
      scheduledIds.add(rule.earlierId);
      scheduledIds.add(rule.laterId);
    });

    const queue = levelNodeIds.filter((id) => indegree.get(id) === 0);
    let seen = 0;

    while (queue.length) {
      const id = queue.shift();
      seen += 1;
      adjacency.get(id).forEach((targetId) => {
        indegree.set(targetId, indegree.get(targetId) - 1);
        if (indegree.get(targetId) === 0) {
          queue.push(targetId);
        }
      });
    }

    if (seen !== levelNodeIds.length) {
      throw new Error(`Scheduling cycle detected on level ${level}.`);
    }

  });

  return { scheduledIds };
}

export function deriveScheduleEdges(nodes, dependencies) {
  const { baseLevels } = computeBaseLevels(nodes, dependencies);
  const nodeOrder = new Map(nodes.map((node, index) => [node.id, index]));
  const groups = new Map();

  nodes.forEach((node) => {
    const startDate = String(node.startDate || "").trim();
    if (!startDate) {
      return;
    }
    const level = baseLevels.get(node.id);
    const key = `${startDate}::${level}`;
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key).push(node.id);
  });

  return [...groups.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .flatMap(([, ids]) => {
      const ordered = [...ids].sort((left, right) => nodeOrder.get(left) - nodeOrder.get(right));
      return ordered.slice(0, -1).map((earlierId, index) => ({
        earlierId,
        laterId: ordered[index + 1],
      }));
    });
}

export function computeGraphLayout(graph) {
  const { nodes, dependencies, schedules } = graph;
  const { baseLevels, parentMap, childMap } = computeBaseLevels(nodes, dependencies);
  const { scheduledIds } = computeScheduleLayout(nodes, schedules, baseLevels);

  const finalLevels = new Map();
  nodes.forEach((node) => {
    const baseLevel = baseLevels.get(node.id) || 0;
    finalLevels.set(node.id, baseLevel);
  });

  const maxLevel = Math.max(...nodes.map((node) => finalLevels.get(node.id)), 0);
  const grouped = new Map();
  nodes.forEach((node) => {
    const level = finalLevels.get(node.id);
    if (!grouped.has(level)) {
      grouped.set(level, []);
    }
    grouped.get(level).push(node.id);
  });

  const positions = new Map();
  [...grouped.entries()]
    .sort(([left], [right]) => left - right)
    .forEach(([level, ids]) => {
      ids.forEach((id, index) => {
        const direction = fibonacciSphere(index, ids.length);
        const radial = maxLevel === 0 ? 0.16 : 0.08 + (level / maxLevel) * 0.88;
        positions.set(id, {
          x: direction.x * radial,
          y: direction.y * radial,
          z: direction.z * radial,
          radial,
          level,
          baseLevel: baseLevels.get(id),
          scheduleOffset: 0,
          scheduled: scheduledIds.has(id),
        });
      });
    });

  return {
    positions,
    parentMap,
    childMap,
    baseLevels,
    finalLevels,
    maxLevel,
    scheduledIds,
  };
}
