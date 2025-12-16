// Méthodes liées aux messages et notifications

export function toggleMessageTab(vm, tab) {
  if (!vm.messageCounts[tab]) {
    const first = (['critical','problem','good']).filter(t => vm.messageCounts[t] > 0)[0];
    if (first) {
      vm.activeMessageTab = first;
      vm.messagesDrawerOpen = true;
    } else {
      vm.messagesDrawerOpen = false;
    }
    return;
  }

  if (vm.activeMessageTab === tab) {
    vm.messagesDrawerOpen = !vm.messagesDrawerOpen;
  } else {
    vm.activeMessageTab = tab;
    vm.messagesDrawerOpen = true;
  }
}

export function dismissMessage(vm, id) {
  if (!id) return;
  if (!vm.dismissedMessageIds.includes(id)) vm.dismissedMessageIds.push(id);
  vm.$nextTick(() => ensureActiveMessageTab(vm));
}

export function dismissMessageBucket(vm, tab) {
  const bucket = vm.messageBuckets[tab] || [];
  bucket.forEach(m => { if (m.id && !vm.dismissedMessageIds.includes(m.id)) vm.dismissedMessageIds.push(m.id); });
  vm.$nextTick(() => ensureActiveMessageTab(vm));
}

export function ensureActiveMessageTab(vm) {
  const counts = vm.messageCounts;
  if (counts[vm.activeMessageTab] > 0) {
    if (vm.messagesDrawerOpen && !vm.currentMessages.length) vm.messagesDrawerOpen = false;
    return;
  }
  const first = (['critical','problem','good']).filter(t => counts[t] > 0)[0];
  if (first) {
    vm.activeMessageTab = first;
    vm.messagesDrawerOpen = false;
  } else {
    vm.messagesDrawerOpen = false;
  }
}

export function dismissChatMessage(vm, index) {
  if (index == null) return;
  vm.messages.splice(index, 1);
}
