
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * Environment variables [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env`. Like [`$env/dynamic/private`](https://kit.svelte.dev/docs/modules#$env-dynamic-private), this module cannot be imported into client-side code. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://kit.svelte.dev/docs/configuration#env) (if configured).
 * 
 * _Unlike_ [`$env/dynamic/private`](https://kit.svelte.dev/docs/modules#$env-dynamic-private), the values exported from this module are statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * ```ts
 * import { API_KEY } from '$env/static/private';
 * ```
 * 
 * Note that all environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * 
 * ```
 * MY_FEATURE_FLAG=""
 * ```
 * 
 * You can override `.env` values from the command line like so:
 * 
 * ```bash
 * MY_FEATURE_FLAG="enabled" npm run dev
 * ```
 */
declare module '$env/static/private' {
	export const ALLUSERSPROFILE: string;
	export const APPDATA: string;
	export const COLOR: string;
	export const CommandPromptType: string;
	export const CommonProgramFiles: string;
	export const CommonProgramW6432: string;
	export const COMPLUS_FusionEnableForcedFullClosureWalk: string;
	export const COMPlus_ThreadPool_UsePortableThreadPool: string;
	export const COMPUTERNAME: string;
	export const ComSpec: string;
	export const DevEnvDir: string;
	export const DOTNET_MULTILEVEL_LOOKUP: string;
	export const DriverData: string;
	export const EDITOR: string;
	export const EFC_10044: string;
	export const ExtensionSdkDir: string;
	export const EXTERNAL_INCLUDE: string;
	export const FPS_BROWSER_APP_PROFILE_STRING: string;
	export const FPS_BROWSER_USER_PROFILE_STRING: string;
	export const Framework40Version: string;
	export const FrameworkDir: string;
	export const FrameworkDir32: string;
	export const FrameworkVersion: string;
	export const FrameworkVersion32: string;
	export const FSHARPINSTALLDIR: string;
	export const GCExpConfigUsedInSession: string;
	export const GOPATH: string;
	export const HOME: string;
	export const HOMEDRIVE: string;
	export const HOMEPATH: string;
	export const IGCCSVC_DB: string;
	export const INCLUDE: string;
	export const INIT_CWD: string;
	export const LIB: string;
	export const LIBPATH: string;
	export const LOCALAPPDATA: string;
	export const LOGONSERVER: string;
	export const MSBuildLoadMicrosoftTargetsReadOnly: string;
	export const NETFXSDKDir: string;
	export const NODE: string;
	export const NODE_ENV: string;
	export const NODE_EXE: string;
	export const NPM_CLI_JS: string;
	export const npm_command: string;
	export const npm_config_cache: string;
	export const npm_config_engine_strict: string;
	export const npm_config_globalconfig: string;
	export const npm_config_global_prefix: string;
	export const npm_config_init_module: string;
	export const npm_config_local_prefix: string;
	export const npm_config_node_gyp: string;
	export const npm_config_noproxy: string;
	export const npm_config_npm_version: string;
	export const npm_config_prefix: string;
	export const npm_config_userconfig: string;
	export const npm_config_user_agent: string;
	export const npm_execpath: string;
	export const npm_lifecycle_event: string;
	export const npm_lifecycle_script: string;
	export const npm_node_execpath: string;
	export const npm_package_json: string;
	export const npm_package_name: string;
	export const npm_package_version: string;
	export const NPM_PREFIX_NPM_CLI_JS: string;
	export const NUMBER_OF_PROCESSORS: string;
	export const OneDrive: string;
	export const OS: string;
	export const Path: string;
	export const PATHEXT: string;
	export const PkgDefApplicationConfigFile: string;
	export const PROCESSOR_ARCHITECTURE: string;
	export const PROCESSOR_IDENTIFIER: string;
	export const PROCESSOR_LEVEL: string;
	export const PROCESSOR_REVISION: string;
	export const ProgramData: string;
	export const ProgramFiles: string;
	export const ProgramW6432: string;
	export const PROMPT: string;
	export const PSModulePath: string;
	export const PUBLIC: string;
	export const ServiceHubClientProcessVersion: string;
	export const ServiceHubCurrentOsLocale: string;
	export const ServiceHubLocationServicePipeName: string;
	export const ServiceHubLogSessionKey: string;
	export const SESSIONNAME: string;
	export const SignInWithHomeTenantOnly: string;
	export const SystemDrive: string;
	export const SystemRoot: string;
	export const TEMP: string;
	export const ThreadedWaitDialogDpiContext: string;
	export const TMP: string;
	export const UCRTVersion: string;
	export const UniversalCRTSdkDir: string;
	export const USERDOMAIN: string;
	export const USERDOMAIN_ROAMINGPROFILE: string;
	export const USERNAME: string;
	export const USERPROFILE: string;
	export const VCIDEInstallDir: string;
	export const VCINSTALLDIR: string;
	export const VCToolsInstallDir: string;
	export const VCToolsRedistDir: string;
	export const VCToolsVersion: string;
	export const VisualStudioDir: string;
	export const VisualStudioEdition: string;
	export const VisualStudioVersion: string;
	export const VS170COMNTOOLS: string;
	export const VSAPPIDDIR: string;
	export const VSAPPIDNAME: string;
	export const VSCMD_ARG_app_plat: string;
	export const VSCMD_ARG_HOST_ARCH: string;
	export const VSCMD_ARG_TGT_ARCH: string;
	export const VSCMD_VER: string;
	export const VSINSTALLDIR: string;
	export const VSLANG: string;
	export const VSLS_SESSION_KEEPALIVE_INTERVAL: string;
	export const VSSKUEDITION: string;
	export const VS_Perf_Session_GCHeapCount: string;
	export const windir: string;
	export const WindowsLibPath: string;
	export const WindowsSdkBinPath: string;
	export const WindowsSdkDir: string;
	export const WindowsSDKLibVersion: string;
	export const WindowsSdkVerBinPath: string;
	export const WindowsSDKVersion: string;
	export const WindowsSDK_ExecutablePath_x64: string;
	export const WindowsSDK_ExecutablePath_x86: string;
	export const ZES_ENABLE_SYSMAN: string;
	export const __DOTNET_ADD_32BIT: string;
	export const __DOTNET_PREFERRED_BITNESS: string;
	export const __VSCMD_PREINIT_PATH: string;
}

/**
 * Similar to [`$env/static/private`](https://kit.svelte.dev/docs/modules#$env-static-private), except that it only includes environment variables that begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Values are replaced statically at build time.
 * 
 * ```ts
 * import { PUBLIC_BASE_URL } from '$env/static/public';
 * ```
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to runtime environment variables, as defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/master/packages/adapter-node) (or running [`vite preview`](https://kit.svelte.dev/docs/cli)), this is equivalent to `process.env`. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://kit.svelte.dev/docs/configuration#env) (if configured).
 * 
 * This module cannot be imported into client-side code.
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * console.log(env.DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 * 
 * > In `dev`, `$env/dynamic` always includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 */
declare module '$env/dynamic/private' {
	export const env: {
		ALLUSERSPROFILE: string;
		APPDATA: string;
		COLOR: string;
		CommandPromptType: string;
		CommonProgramFiles: string;
		CommonProgramW6432: string;
		COMPLUS_FusionEnableForcedFullClosureWalk: string;
		COMPlus_ThreadPool_UsePortableThreadPool: string;
		COMPUTERNAME: string;
		ComSpec: string;
		DevEnvDir: string;
		DOTNET_MULTILEVEL_LOOKUP: string;
		DriverData: string;
		EDITOR: string;
		EFC_10044: string;
		ExtensionSdkDir: string;
		EXTERNAL_INCLUDE: string;
		FPS_BROWSER_APP_PROFILE_STRING: string;
		FPS_BROWSER_USER_PROFILE_STRING: string;
		Framework40Version: string;
		FrameworkDir: string;
		FrameworkDir32: string;
		FrameworkVersion: string;
		FrameworkVersion32: string;
		FSHARPINSTALLDIR: string;
		GCExpConfigUsedInSession: string;
		GOPATH: string;
		HOME: string;
		HOMEDRIVE: string;
		HOMEPATH: string;
		IGCCSVC_DB: string;
		INCLUDE: string;
		INIT_CWD: string;
		LIB: string;
		LIBPATH: string;
		LOCALAPPDATA: string;
		LOGONSERVER: string;
		MSBuildLoadMicrosoftTargetsReadOnly: string;
		NETFXSDKDir: string;
		NODE: string;
		NODE_ENV: string;
		NODE_EXE: string;
		NPM_CLI_JS: string;
		npm_command: string;
		npm_config_cache: string;
		npm_config_engine_strict: string;
		npm_config_globalconfig: string;
		npm_config_global_prefix: string;
		npm_config_init_module: string;
		npm_config_local_prefix: string;
		npm_config_node_gyp: string;
		npm_config_noproxy: string;
		npm_config_npm_version: string;
		npm_config_prefix: string;
		npm_config_userconfig: string;
		npm_config_user_agent: string;
		npm_execpath: string;
		npm_lifecycle_event: string;
		npm_lifecycle_script: string;
		npm_node_execpath: string;
		npm_package_json: string;
		npm_package_name: string;
		npm_package_version: string;
		NPM_PREFIX_NPM_CLI_JS: string;
		NUMBER_OF_PROCESSORS: string;
		OneDrive: string;
		OS: string;
		Path: string;
		PATHEXT: string;
		PkgDefApplicationConfigFile: string;
		PROCESSOR_ARCHITECTURE: string;
		PROCESSOR_IDENTIFIER: string;
		PROCESSOR_LEVEL: string;
		PROCESSOR_REVISION: string;
		ProgramData: string;
		ProgramFiles: string;
		ProgramW6432: string;
		PROMPT: string;
		PSModulePath: string;
		PUBLIC: string;
		ServiceHubClientProcessVersion: string;
		ServiceHubCurrentOsLocale: string;
		ServiceHubLocationServicePipeName: string;
		ServiceHubLogSessionKey: string;
		SESSIONNAME: string;
		SignInWithHomeTenantOnly: string;
		SystemDrive: string;
		SystemRoot: string;
		TEMP: string;
		ThreadedWaitDialogDpiContext: string;
		TMP: string;
		UCRTVersion: string;
		UniversalCRTSdkDir: string;
		USERDOMAIN: string;
		USERDOMAIN_ROAMINGPROFILE: string;
		USERNAME: string;
		USERPROFILE: string;
		VCIDEInstallDir: string;
		VCINSTALLDIR: string;
		VCToolsInstallDir: string;
		VCToolsRedistDir: string;
		VCToolsVersion: string;
		VisualStudioDir: string;
		VisualStudioEdition: string;
		VisualStudioVersion: string;
		VS170COMNTOOLS: string;
		VSAPPIDDIR: string;
		VSAPPIDNAME: string;
		VSCMD_ARG_app_plat: string;
		VSCMD_ARG_HOST_ARCH: string;
		VSCMD_ARG_TGT_ARCH: string;
		VSCMD_VER: string;
		VSINSTALLDIR: string;
		VSLANG: string;
		VSLS_SESSION_KEEPALIVE_INTERVAL: string;
		VSSKUEDITION: string;
		VS_Perf_Session_GCHeapCount: string;
		windir: string;
		WindowsLibPath: string;
		WindowsSdkBinPath: string;
		WindowsSdkDir: string;
		WindowsSDKLibVersion: string;
		WindowsSdkVerBinPath: string;
		WindowsSDKVersion: string;
		WindowsSDK_ExecutablePath_x64: string;
		WindowsSDK_ExecutablePath_x86: string;
		ZES_ENABLE_SYSMAN: string;
		__DOTNET_ADD_32BIT: string;
		__DOTNET_PREFERRED_BITNESS: string;
		__VSCMD_PREINIT_PATH: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * Similar to [`$env/dynamic/private`](https://kit.svelte.dev/docs/modules#$env-dynamic-private), but only includes variables that begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Note that public dynamic environment variables must all be sent from the server to the client, causing larger network requests — when possible, use `$env/static/public` instead.
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.PUBLIC_DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
