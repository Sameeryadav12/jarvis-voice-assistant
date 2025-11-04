; Inno Setup Script for Jarvis Voice Assistant
; Requires Inno Setup 6.0 or later
; Download: https://jrsoftware.org/isdl.php

#define MyAppName "Jarvis Voice Assistant"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Jarvis Team"
#define MyAppURL "https://github.com/jarvis-assistant/jarvis"
#define MyAppExeName "jarvis_ui.exe"
#define MyAppConsoleExeName "jarvis_simple.exe"

[Setup]
; Application information
AppId={{8F9C4D2E-5A3B-4E8F-9D1C-7B6E4A2F8C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\Jarvis
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output
OutputDir=..\dist
OutputBaseFilename=JarvisSetup_{#MyAppVersion}
SetupIconFile=..\assets\jarvis_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes

; Windows version requirements
MinVersion=10.0.19041
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; UI
WizardStyle=modern
DisableWelcomePage=no
LicenseFile=..\LICENSE
InfoBeforeFile=..\README.md

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "autostart"; Description: "Run Jarvis on Windows startup"; GroupDescription: "Additional options:"; Flags: checked
Name: "vcredist"; Description: "Install Visual C++ Redistributable (required)"; GroupDescription: "Dependencies:"; Flags: checked
Name: "downloadmodels"; Description: "Download voice models (recommended, ~500MB)"; GroupDescription: "Optional components:"; Flags: unchecked

[Files]
; Main executable
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\{#MyAppConsoleExeName}"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('..\dist\{#MyAppConsoleExeName}'))

; Core files
Source: "..\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\apps\*"; DestDir: "{app}\apps"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

; Assets
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; VC++ Redistributable (bundle with installer)
; Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
Source: "dependencies\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: VCRedistNeedsInstall and IsTaskSelected('vcredist')

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} (Console)"; Filename: "{app}\{#MyAppConsoleExeName}"; Check: FileExists(ExpandConstant('{app}\{#MyAppConsoleExeName}'))
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Autostart
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "JarvisAssistant"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: autostart

; File associations (optional - for .jarvis files)
Root: HKCR; Subkey: ".jarvis"; ValueType: string; ValueName: ""; ValueData: "JarvisScript"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "JarvisScript"; ValueType: string; ValueName: ""; ValueData: "Jarvis Script"; Flags: uninsdeletekey
Root: HKCR; Subkey: "JarvisScript\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCR; Subkey: "JarvisScript\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Run]
; Install VC++ Redistributable
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installing Visual C++ Redistributable..."; Flags: waituntilterminated; Check: VCRedistNeedsInstall and IsTaskSelected('vcredist')

; Download voice models (optional)
Filename: "{app}\{#MyAppConsoleExeName}"; Parameters: "--download-models"; StatusMsg: "Downloading voice models..."; Flags: postinstall skipifsilent runhidden; Check: IsTaskSelected('downloadmodels') and FileExists(ExpandConstant('{app}\{#MyAppConsoleExeName}'))

; Launch application
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Clean up user data (optional)
Filename: "{app}\{#MyAppConsoleExeName}"; Parameters: "--cleanup"; Flags: runhidden waituntilterminated; Check: FileExists(ExpandConstant('{app}\{#MyAppConsoleExeName}'))

[Code]
function VCRedistNeedsInstall: Boolean;
var
  Version: String;
begin
  // Check if VC++ 2015-2022 Redistributable is installed
  if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version) then
  begin
    // Version is installed, check if it's recent enough
    Result := (Version < 'v14.30.0.0');
  end
  else
  begin
    // Not installed
    Result := True;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create user config directory
    CreateDir(ExpandConstant('{userappdata}\Jarvis'));
    CreateDir(ExpandConstant('{userappdata}\Jarvis\config'));
    CreateDir(ExpandConstant('{userappdata}\Jarvis\logs'));
    CreateDir(ExpandConstant('{userappdata}\Jarvis\models'));
  end;
end;

procedure InitializeWizard;
begin
  // Custom welcome message
  WizardForm.WelcomeLabel2.Caption := 
    'This will install ' + '{#MyAppName}' + ' on your computer.' + #13#10 + #13#10 +
    'Jarvis is an AI-powered voice assistant with natural language understanding, ' +
    'calendar integration, and smart automation.' + #13#10 + #13#10 +
    'Click Next to continue, or Cancel to exit Setup.';
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check Windows version
  if not (GetWindowsVersion >= $0A000000) then
  begin
    MsgBox('This application requires Windows 10 (version 1809 or later).', mbError, MB_OK);
    Result := False;
  end;
end;

