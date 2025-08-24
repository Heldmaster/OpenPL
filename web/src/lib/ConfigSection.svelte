<script>
	export let data;
	export let level = 0;
	export let parentKey = '';

	function getType(value) {
		if (Array.isArray(value)) return 'array';
		if (value === null) return 'null';
		if (typeof value === 'object') return 'object';
		return typeof value;
	}

	function formatValue(value) {
		const type = getType(value);

		switch (type) {
			case 'string':
				return value;
			case 'boolean':
				return value ? 'true' : 'false';
			case 'number':
				return value.toString();
			case 'null':
				return 'null';
			case 'undefined':
				return 'undefined';
			default:
				return '';
		}
	}

	function getValueClass(value) {
		const type = getType(value);
		return `value value-${type}`;
	}

	function getFullKey(key) {
		return parentKey ? `${parentKey}.${key}` : key;
	}
</script>

<div class="config-display" class:level-{level}>
	{#if Array.isArray(data)}
		<div class="array-container">
			<div class="section-content">
				{#each data as item, index}
					<div class="array-item">
						<div class="item-header">
							<span class="item-index">[{index}]</span>
							{#if Array.isArray(item) || (typeof item === 'object' && item !== null)}
								<span class="item-type">{getType(item)}</span>
							{/if}
						</div>

						{#if Array.isArray(item) || (typeof item === 'object' && item !== null)}
							<svelte:self data={item} level={level + 1} parentKey={getFullKey(`[${index}]`)} />
						{:else}
							<div class="simple-value">
								<span class={getValueClass(item)}>{formatValue(item)}</span>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{:else if typeof data === 'object' && data !== null}
		<div class="object-container">
			<div class="section-content">
				{#each Object.entries(data) as [key, value]}
					<div class="property">
						<div class="property-header">
							<span class="property-key">{key}</span>
							{#if getType(value) === 'array'}
								<span class="property-count">({value.length})</span>
							{/if}
						</div>

						{#if Array.isArray(value) || (typeof value === 'object' && value !== null)}
							<svelte:self data={value} level={level + 1} parentKey={getFullKey(key)} />
						{:else}
							<div class="property-value">
								<span class={getValueClass(value)}>{formatValue(value)}</span>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{:else}
		<div class="primitive-value">
			<span class={getValueClass(data)}>{formatValue(data)}</span>
		</div>
	{/if}
</div>

<style>
	.config-display {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	/* Уровни вложенности */
	.level-0 {
		--indent: 0px;
	}
	.level-1 {
		--indent: 20px;
	}
	.level-2 {
		--indent: 40px;
	}
	.level-3 {
		--indent: 60px;
	}
	.level-4 {
		--indent: 80px;
	}

	.section-header {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 12px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border-radius: 8px;
		margin-bottom: 8px;
		font-weight: 500;
	}

	.section-title {
		font-weight: 600;
	}

	.section-count {
		font-size: 12px;
		opacity: 0.9;
	}

	.section-content {
		margin-left: var(--indent);
		padding-left: 16px;
		border-left: 2px solid #e1e5e9;
	}

	.array-item,
	.property {
		margin: 12px 0;
		padding: 12px;
		background: white;
		border-radius: 8px;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		border: 1px solid #e1e5e9;
	}

	.item-header,
	.property-header {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 8px;
		padding-bottom: 8px;
		border-bottom: 1px solid #f0f0f0;
	}

	.item-index {
		font-weight: 600;
		color: #6b46c1;
		background: #f0ebff;
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 12px;
	}

	.property-key {
		font-weight: 600;
		color: #2d3748;
		background: #edf2f7;
		padding: 4px 10px;
		border-radius: 6px;
		font-family: 'Monaco', 'Consolas', monospace;
		font-size: 13px;
	}

	.property-type,
	.item-type {
		font-size: 11px;
		color: #718096;
		background: #f7fafc;
		padding: 2px 6px;
		border-radius: 4px;
		text-transform: uppercase;
		font-weight: 500;
	}

	.property-count {
		font-size: 11px;
		color: #48bb78;
		background: #f0fff4;
		padding: 2px 6px;
		border-radius: 4px;
	}

	.simple-value,
	.property-value,
	.primitive-value {
		padding: 8px 12px;
		border-radius: 6px;
		margin: 4px 0;
		font-family: 'Monaco', 'Consolas', monospace;
		font-size: 14px;
	}

	.value {
		display: inline-block;
		padding: 6px 10px;
		border-radius: 5px;
		font-weight: 500;
		border: 1px solid;
	}

	.value-string {
		color: #c53030;
		background: #fed7d7;
		border-color: #feb2b2;
	}

	.value-number {
		color: #2b6cb0;
		background: #bee3f8;
		border-color: #90cdf4;
	}

	.value-boolean {
		color: #276749;
		background: #c6f6d5;
		border-color: #9ae6b4;
	}

	.value-null {
		color: #4a5568;
		background: #e2e8f0;
		border-color: #cbd5e0;
		font-style: italic;
	}

	.value-undefined {
		color: #718096;
		background: #f7fafc;
		border-color: #e2e8f0;
		font-style: italic;
	}

	.section-icon {
		font-size: 16px;
	}

	/* Анимации */
	.array-item,
	.property {
		transition: all 0.2s ease;
	}

	.array-item:hover,
	.property:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		transform: translateY(-1px);
	}

	/* Responsive */
	@media (max-width: 768px) {
		.section-header {
			flex-wrap: wrap;
		}

		.item-header,
		.property-header {
			flex-wrap: wrap;
			gap: 4px;
		}

		.section-content {
			margin-left: 10px;
			padding-left: 10px;
		}
	}
</style>
