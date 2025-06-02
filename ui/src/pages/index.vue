<template>
    <div
        class="d-flex ga-0 overflow-y-hidden"
        style="height: 100vh;"
    >
        <div
            class="d-flex flex-column w-50"
        >
            <v-toolbar 
                border 
                density="comfortable"
            >
                <v-tooltip
                    location="top"
                    text="Evaluate a single Python expression"
                >
                    <template
                        v-slot:activator="{ props }"
                    >
                        <v-btn
                            v-bind="props"
                            :color="mode === 'eval' ? 'primary' : ''"
                            icon="mdi-math-integral-box"
                            @click="mode = 'eval'"
                        />
                    </template>
                </v-tooltip>
                <v-tooltip
                    location="top"
                    text="Execute a series of Python statements"
                >
                    <template
                        v-slot:activator="{ props }"
                    >
                        <v-btn
                            v-bind="props"
                            :color="mode === 'exec' ? 'primary' : ''"
                            icon="mdi-code-braces-box"
                            @click="mode = 'exec'"
                        />
                    </template>
                </v-tooltip>
                <v-divider
                    vertical
                />
                <v-tooltip
                    location="top"
                    text="Add an element to the results list"
                >
                    <template
                        v-slot:activator="{ props }"
                    >
                        <v-btn
                            v-bind="props"
                            :disabled="mode !== 'exec'"
                            icon="mdi-code-block-brackets"
                            @click="handleAddElementToResultsList"
                        />
                    </template>
                </v-tooltip>
                <v-tooltip
                    location="top"
                    text="Set a value in the results dict"
                >
                    <template
                        v-slot:activator="{ props }"
                    >
                        <v-btn
                            v-bind="props"
                            :disabled="mode !== 'exec'"
                            icon="mdi-code-block-braces"
                            @click="handleAddValueToResultsDict"
                        />
                    </template>
                </v-tooltip>
                <v-divider
                    vertical
                />
                <v-tooltip
                    location="top"
                    text="Send All to TS4 and Run"
                >
                    <template
                        v-slot:activator="{ props }"
                    >
                        <v-btn
                            v-bind="props"
                            color="success"
                            icon="mdi-run"
                            @click="handleSendAllAndRun"
                        />
                    </template>
                </v-tooltip>
                <v-tooltip
                    location="top"
                    text="Send Selected to TS4 and Run"
                >
                    <template
                        v-slot:activator="{ props }"
                    >
                        <v-btn
                            v-bind="props"
                            color="success"
                            icon="mdi-run-fast"
                            @click="handleSendSelectionAndRun"
                        />
                    </template>
                </v-tooltip>
            </v-toolbar>
            <div
                class="flex-grow-1"
            >
                <v-textarea
                    ref="editor"
                    v-model="code"
                    class="h-100 monospace mt-3 mx-2"
                    label="Python"
                    variant="outlined"
                />
            </div>
        </div>
        <div
            ref="responsesContainer"
            class="flex-grow-1 overflow-y-auto w-50"
            style="scroll-behavior: smooth;"
        >
            <div
                class="d-flex flex-column ga-2 ma-2"
            >
                <v-card
                    v-for="response in responses"
                    :color="response.thrown ? 'error' : ''"
                    :prepend-icon="response.type === 'exec_result' ? 'mdi-code-braces-box' : 'mdi-math-integral-box'"
                    :subtitle="response.thrown ? 'This operation raised an error.' : ''"
                    :title="response.type === 'exec_result' ? 'Execution Result' : response.type === 'eval_result' ? 'Evaluation Result' : 'Unrecognized Response'"
                    variant="tonal"
                >
                    <v-card
                        v-if="response.thrown"
                        class="mx-2 mb-2"
                        color="error"
                        variant="oulined"
                    >
                        <pre class="pa-2">{{ response.thrown }}</pre>
                    </v-card>
                    <v-table
                        v-if="!response.thrown && response.type === 'exec_result' && response.results_list && response.results_list.length"
                        class="mx-2 mb-2"
                        density="compact"
                    >
                        <thead>
                            <tr>
                                <th
                                >
                                    Value
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="element in response.results_list"
                            >
                                <td>
                                    <code>{{ JSON.stringify(element) }}</code>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                    <v-table
                        v-if="!response.thrown && response.type === 'exec_result' && response.results_dict && Object.keys(response.results_dict).length"
                        class="mx-2 mb-2"
                        density="compact"
                    >
                        <thead>
                            <tr>
                                <th
                                >
                                    Attribute
                                </th>
                                <th
                                >
                                    Value
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="key in Object.keys(response.results_dict)"
                            >
                                <td>
                                    <code>{{ JSON.stringify(key) }}</code>
                                </td>
                                <td>
                                    <code>{{ JSON.stringify(response.results_dict[key]) }}</code>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                    <v-card
                        v-if="!response.thrown && response.type === 'eval_result'"
                        class="mx-2 mb-2"
                        variant="oulined"
                    >
                        <code class="px-2">{{ JSON.stringify(response.eval_result) }}</code>
                    </v-card>
                </v-card>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, shallowRef } from 'vue';

    const MONACO_EDITOR_OPTIONS = {
        automaticLayout: true,
        formatOnType: true,
        formatOnPaste: true,
    }

    const mode = ref('eval');
    const code = ref('');
    const editor = ref(null);
    const responses = ref([]);
    const responsesContainer = ref(null);

    function getSelectedCode() {
        const ed = editor.value;
        return ed.value.slice(ed.selectionStart, ed.selectionEnd);
    }

    function replaceSelectedCode(replacement) {
        const pyCode = code.value;
        const ed = editor.value;
        code.value = `${pyCode.slice(0, ed.selectionStart)}${replacement}${pyCode.slice(ed.selectionEnd)}`;
    }

    function handleAddElementToResultsList() {
        replaceSelectedCode(`__EXEC_RESULTS_LIST__.append(${getSelectedCode()})`);
    }

    function handleAddValueToResultsDict() {
        replaceSelectedCode(`__EXEC_RESULTS_DICT__[''] = ${getSelectedCode()}`);
    }
    
    function handleSendAllAndRun() {
        gateway.announce({
            type: mode.value,
            code: code.value,
        });
    }

    function handleSendSelectionAndRun() {
        gateway.announce({
            type: mode.value,
            code: getSelectedCode(),
        });
    }

    function handleDataReceived(data) {
        responses.value = [...responses.value, data];
        setTimeout(() => responsesContainer.value.scrollTop = responsesContainer.value.scrollHeight, 0);
    }

    if (typeof gateway !== 'undefined') {
        gateway.dataReceived.addListener(handleDataReceived);
    }
</script>

<style>
    .monospace {
        font-family: monospace;
    }
</style>