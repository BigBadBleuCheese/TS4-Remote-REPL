<template>
    <div
        class="d-flex ga-0 overflow-y-hidden"
        style="height: 100vh;"
    >
        <div
            class="d-flex flex-column w-50"
        >
            <v-toolbar
                density="comfortable"
                image="../assets/toolbar-background.gif"
                title="Remote REPL"
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
                            class="ma-1"
                            :color="persistedState.mode === 'eval' ? 'primary' : ''"
                            icon="mdi-math-integral-box"
                            variant="flat"
                            size="small"
                            @click="persistedState.mode = 'eval'"
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
                            class="ma-1"
                            :color="persistedState.mode === 'exec' ? 'primary' : ''"
                            icon="mdi-code-braces-box"
                            variant="flat"
                            size="small"
                            @click="persistedState.mode = 'exec'"
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
                            class="ma-1"
                            :disabled="persistedState.mode !== 'exec'"
                            icon="mdi-code-block-brackets"
                            variant="flat"
                            size="small"
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
                            class="ma-1"
                            :disabled="persistedState.mode !== 'exec'"
                            icon="mdi-code-block-braces"
                            variant="flat"
                            size="small"
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
                            class="ma-1"
                            color="success"
                            icon="mdi-run"
                            variant="flat"
                            size="small"
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
                            class="ma-1"
                            color="success"
                            icon="mdi-run-fast"
                            variant="flat"
                            size="small"
                            @click="handleSendSelectionAndRun"
                        />
                    </template>
                </v-tooltip>
            </v-toolbar>
            <div
                class="flex-grow-1"
            >
                <vue-monaco-editor
                    v-model:value="persistedState.code"
                    language="python"
                    :options="MONACO_EDITOR_OPTIONS"
                    theme="vs-dark"
                    @mount="handleMount"
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
                    <v-card
                        v-if="!response.thrown && response.type === 'eval_result'"
                        class="mx-2 mb-2"
                        variant="oulined"
                    >
                        <highlightjs
                            :code="JSON.stringify(response.eval_result, null, 4)"
                            language="js"
                        />
                    </v-card>
                    <v-card
                        v-if="!response.thrown && response.type === 'exec_result' && response.results_list && response.results_list.length"
                        class="mx-2 mb-2"
                        variant="oulined"
                    >
                        <highlightjs
                            :code="JSON.stringify(response.results_list, null, 4)"
                            language="js"
                        />
                    </v-card>
                    <v-card
                        v-if="!response.thrown && response.type === 'exec_result' && response.results_dict && Object.keys(response.results_dict).length"
                        class="mx-2 mb-2"
                        variant="oulined"
                    >
                        <highlightjs
                            :code="JSON.stringify(response.results_dict, null, 4)"
                            language="js"
                        />
                    </v-card>
                </v-card>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, shallowRef } from 'vue';
    import { usePersistedState } from '@/stores/global-state';

    const persistedState = usePersistedState();

    const MONACO_EDITOR_OPTIONS = {
        automaticLayout: true,
        formatOnType: true,
        formatOnPaste: true,
    }

    const editor = shallowRef();
    const responses = ref([]);
    const responsesContainer = ref(null);

    function handleMount(editorInstance) {
        editor.value = editorInstance;
    }

    function getSelectedCode() {
        const ed = editor.value;
        return ed.getModel().getValueInRange(ed.getSelection());
    }

    function replaceSelectedCode(replacement) {
        const ed = editor.value;
        ed.executeEdits('replace', [
            {
                range: ed.getSelection(),
                text: replacement,
                forceMoveMarkers: true,
            }
        ]);
    }

    function handleAddElementToResultsList() {
        replaceSelectedCode(`__EXEC_RESULTS_LIST__.append(${getSelectedCode()})`);
    }

    function handleAddValueToResultsDict() {
        replaceSelectedCode(`__EXEC_RESULTS_DICT__[''] = ${getSelectedCode()}`);
    }
    
    function handleSendAllAndRun() {
        gateway.announce({
            type: persistedState.mode.value,
            code: persistedState.code.value,
        });
    }

    function handleSendSelectionAndRun() {
        gateway.announce({
            type: persistedState.mode.value,
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