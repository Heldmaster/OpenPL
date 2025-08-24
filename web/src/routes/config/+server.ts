import { json } from '@sveltejs/kit'
import fs from 'fs/promises'
import path from 'path'
import toml from '@iarna/toml'

const CONFIG_PATH = path.join(process.cwd(), '..', 'src', 'cfg', 'config.toml')

export async function GET() {
	try {
		const configContent = await fs.readFile(CONFIG_PATH, 'utf-8')
		const configData = toml.parse(configContent)
		return json({ success: true, data: configData })
	} catch (error) {
		return json(
			{
				success: false,
				error: 'Failed to read config file',
				details: error.message
			},
			{ status: 500 }
		)
	}
}

export async function POST({ request }) {
	try {
		const { config } = await request.json()

		if (!config || typeof config !== 'object') {
			return json(
				{
					success: false,
					error: 'Invalid config data'
				},
				{ status: 400 }
			)
		}

		const tomlString = toml.stringify(config)

		await fs.writeFile(CONFIG_PATH, tomlString, 'utf-8')

		return json({ success: true, message: 'Config updated successfully' })
	} catch (error) {
		return json(
			{
				success: false,
				error: 'Failed to update config',
				details: error.message
			},
			{ status: 500 }
		)
	}
}
