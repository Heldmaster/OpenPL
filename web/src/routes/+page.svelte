<script>
	import ConfigSection from '$lib/ConfigSection.svelte';
	import { onMount } from 'svelte';

	let configData = null;
	let loading = true;
	let error = null;
	let successMessage = '';
	let editMode = false;
	let editedConfig = '';
	let saving = false;

	async function loadConfig() {
		try {
			loading = true;
			error = null;
			const response = await fetch('/config');

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();

			if (result.success) {
				configData = result.data;
				editedConfig = JSON.stringify(result.data, null, 2);
			} else {
				throw new Error(result.error || 'Failed to load config');
			}
		} catch (err) {
			error = err.message;
			console.error('Error loading config:', err);
		} finally {
			loading = false;
		}
	}

	function enableEdit() {
		editMode = true;
		editedConfig = JSON.stringify(configData, null, 2);
	}

	function cancelEdit() {
		editMode = false;
		error = null;
		successMessage = '';
	}

	async function saveConfig() {
		try {
			saving = true;
			error = null;
			successMessage = '';

			const parsedConfig = JSON.parse(editedConfig);

			const response = await fetch('/config', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ config: parsedConfig })
			});

			const result = await response.json();

			if (result.success) {
				configData = parsedConfig;
				editMode = false;

				setTimeout(() => loadConfig(), 500);
			} else {
				throw new Error(result.error || 'Failed to save config');
			}
		} catch (err) {
			error = err.message;
			console.error('Error saving config:', err);
		} finally {
			saving = false;
		}
	}

	onMount(() => {
		loadConfig();
	});
</script>

<main class="config-page">
	<div class="header">
		<h1>Configuration Editor</h1>
		<div class="actions">
			{#if !editMode}
				<button on:click={enableEdit} class="btn btn-primary"> Edit Configuration </button>
			{:else}
				<button on:click={cancelEdit} class="btn btn-secondary"> Cancel </button>
				<button on:click={saveConfig} disabled={saving} class="btn btn-primary">
					{saving ? 'Saving...' : 'Save Changes'}
				</button>
			{/if}
			<button on:click={loadConfig} class="btn btn-secondary"> Refresh </button>
		</div>
	</div>

	{#if loading}
		<div class="loading">Loading configuration...</div>
	{:else if error}
		<div class="error">
			<h3>Error</h3>
			<p>{error}</p>
			<button on:click={loadConfig} class="btn btn-secondary"> Try Again </button>
		</div>
	{:else if configData}
		{#if editMode}
			<div class="edit-mode">
				<div class="editor-header">
					<h2>Edit Configuration (JSON format)</h2>
					<p class="hint">Modify the JSON below and click "Save Changes"</p>
				</div>

				<textarea
					bind:value={editedConfig}
					class="config-editor"
					placeholder="Paste your configuration JSON here..."
					rows={20}
				></textarea>

				{#if error}
					<div class="error">{error}</div>
				{/if}
			</div>
		{:else}
			<div class="view-mode">
				<h2>Current Configuration</h2>
				<div class="config-display-container">
					<ConfigSection data={configData} />
				</div>
			</div>
		{/if}
	{:else}
		<div class="no-data">No configuration data available</div>
	{/if}
</main>

<style>
	.config-page {
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30px;
		padding-bottom: 20px;
		border-bottom: 2px solid #e0e0e0;
	}

	h1 {
		color: #333;
		margin: 0;
		font-size: 28px;
	}

	h2 {
		color: #444;
		margin: 0 0 20px 0;
		font-size: 22px;
	}

	.actions {
		display: flex;
		gap: 10px;
	}

	.btn {
		padding: 10px 20px;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 14px;
		font-weight: 500;
		transition: all 0.2s ease;
	}

	.btn-primary {
		background-color: #007bff;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #0056b3;
	}

	.btn-primary:disabled {
		background-color: #6c757d;
		cursor: not-allowed;
	}

	.btn-secondary {
		background-color: #6c757d;
		color: white;
	}

	.btn-secondary:hover {
		background-color: #545b62;
	}

	.loading,
	.no-data {
		text-align: center;
		padding: 40px;
		color: #666;
		font-size: 18px;
	}

	.error {
		background-color: #f8d7da;
		color: #721c24;
		padding: 15px;
		border-radius: 6px;
		margin: 20px 0;
		border: 1px solid #f5c6cb;
	}

	.edit-mode {
		margin-top: 20px;
	}

	.editor-header {
		margin-bottom: 20px;
	}

	.hint {
		color: #666;
		font-size: 14px;
		margin: 5px 0 0 0;
	}

	.config-editor {
		width: 100%;
		padding: 15px;
		border: 2px solid #ddd;
		border-radius: 6px;
		font-family: 'Monaco', 'Consolas', monospace;
		font-size: 14px;
		line-height: 1.5;
		resize: vertical;
		min-height: 400px;
	}

	.config-editor:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
	}

	.view-mode {
		margin-top: 20px;
	}

	.config-display-container {
		background-color: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 6px;
		padding: 20px;
		overflow-x: auto;
	}
</style>
