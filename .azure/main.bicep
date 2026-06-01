// ============================================================================
// Aria Platform - Production Infrastructure
// ============================================================================
// This Bicep template deploys the complete Aria platform to Azure:
// - Azure Functions (primary API endpoint)
// - Azure Container Apps (optional Aria web server)
// - Azure SQL Database (QAI_DB_CONN)
// - Azure Cosmos DB (optional semantic memory)
// - Application Insights (telemetry)
// - Key Vault (secrets management)

metadata name = 'Aria Platform Deployment'
metadata description = 'Complete infrastructure for Aria interactive AI character platform'
metadata owner = 'Platform Team'

// ============================================================================
// Parameters
// ============================================================================

@description('Azure region for all resources')
param location string = 'eastus'

@description('Environment name (prod, staging, dev)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'prod'

@description('Function App name')
param functionAppName string = 'aria-${environment}'

@description('Storage account name (must be globally unique, lowercase)')
param storageAccountName string = 'aria${environment}${uniqueString(resourceGroup().id)}'

@description('SQL Server name (must be globally unique)')
param sqlServerName string = 'aria-${environment}-sql-${uniqueString(resourceGroup().id)}'

@description('SQL admin username')
param sqlAdminUsername string = 'sqladmin'

@description('SQL admin password (should be from Key Vault)')
@secure()
param sqlAdminPassword string

@description('Cosmos DB account name (optional)')
param cosmosAccountName string = 'aria-${environment}-cosmos-${uniqueString(resourceGroup().id)}'

@description('Enable Cosmos DB deployment')
param enableCosmos bool = true

@description('Container registry name for pulling images')
param containerRegistryName string = ''

@description('Container image URI for Functions')
param functionImageUri string = '${containerRegistryName}.azurecr.io/functions:latest'

@description('Application Insights name')
param appInsightsName string = 'aria-${environment}-insights'

@description('Key Vault name')
param keyVaultName string = 'aria-${environment}-kv-${uniqueString(resourceGroup().id)}'

@description('Deployment tags')
param tags object = {
  environment: environment
  platform: 'aria'
  deploymentDate: utcNow('u')
}

// ============================================================================
// Variables
// ============================================================================

var appServicePlanName = '${functionAppName}-plan'
var cosmosDbDatabaseName = 'aria'
var cosmosDbContainerName = 'chat-sessions'
var sqlDatabaseName = 'aria_${environment}'
var appInsightsWorkspaceName = 'aria-${environment}-workspace'

// ============================================================================
// Storage Account
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
  tags: tags
}

// ============================================================================
// Application Insights
// ============================================================================

resource appInsightsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: appInsightsWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
  tags: tags
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: appInsightsWorkspace.id
    RetentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: tags
}

// ============================================================================
// Key Vault
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
  tags: tags
}

// ============================================================================
// SQL Database
// ============================================================================

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdminUsername
    administratorLoginPassword: sqlAdminPassword
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
  tags: tags
}

resource sqlServerFirewall 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
    capacity: 10 // 10 DTU
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 268435456000 // 250 GB
  }
  tags: tags
}

resource sqlDatabaseBackupRetention 'Microsoft.Sql/servers/databases/backupShortTermRetentionPolicies@2023-08-01-preview' = {
  parent: sqlDatabase
  name: 'default'
  properties: {
    retentionDays: 7
    diffBackupIntervalInHours: 24
  }
}

// ============================================================================
// Cosmos DB (Optional)
// ============================================================================

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = if (enableCosmos) {
  name: cosmosAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        failoverPriority: 0
        locationName: location
      }
    ]
    enableFreeTier: false
    defaultIdentityType: 'FirstPartyIdentity'
    minimalTlsVersion: 'Tls12'
  }
  tags: tags
}

resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = if (enableCosmos) {
  parent: cosmosAccount
  name: cosmosDbDatabaseName
  properties: {
    resource: {
      id: cosmosDbDatabaseName
    }
  }
}

resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = if (enableCosmos) {
  parent: cosmosDatabase
  name: cosmosDbContainerName
  properties: {
    resource: {
      id: cosmosDbContainerName
      partitionKey: {
        paths: [
          '/session_id'
        ]
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
      }
      ttl: 2592000 // 30 days in seconds
    }
    options: {
      throughput: 400 // Minimum RU/s
    }
  }
}

// ============================================================================
// App Service Plan (Functions)
// ============================================================================

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  kind: 'elastic'
  sku: {
    name: 'EP1'
    tier: 'ElasticPremium'
    size: 'EP1'
    family: 'EP'
    capacity: 1
  }
  properties: {
    targetWorkerCount: 1
    maximumElasticWorkerCount: 10
  }
  tags: tags
}

// ============================================================================
// Azure Functions
// ============================================================================

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      numberOfWorkers: 1
      defaultDocuments: []
      netFrameworkVersion: 'v6.0'
      requestTracingEnabled: true
      remoteDebuggingEnabled: false
      httpLoggingEnabled: true
      detailedErrorLoggingEnabled: true
      publishingUsername: '${functionAppName}'
      scmType: 'None'
      use32BitWorkerProcess: false
      webSocketsEnabled: false
      managedPipelineMode: 'Integrated'
      virtualApplications: [
        {
          virtualPath: '/'
          physicalPath: 'site\\wwwroot'
          preloadEnabled: true
        }
      ]
      loadBalancing: 'LeastRequests'
      experiments: {
        rampUpRules: []
      }
      autoHealEnabled: true
      localMySqlEnabled: false
      ipSecurityRestrictions: [
        {
          ipAddress: 'Any'
          action: 'Allow'
          priority: 1
          name: 'Allow all'
          description: 'Allow all access'
        }
      ]
      scmIpSecurityRestrictions: [
        {
          ipAddress: 'Any'
          action: 'Allow'
          priority: 1
          name: 'Allow all'
          description: 'Allow all access'
        }
      ]
      scmIpSecurityRestrictionsUseMain: false
      http20Enabled: true
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.0'
      linuxFxVersion: 'DOCKER|${functionImageUri}'
      preWarmedInstanceCount: 1
      functionAppScaleLimit: 0
      healthCheckPath: '/api/ai/status'
      fileChangeAuditEnabled: false
      functionsRuntimeScaleMonitoringEnabled: false
      websiteTimeZone: 'UTC'
      minimumElasticInstanceCount: 1
    }
    httpsOnly: true
  }
  tags: tags
}

// ============================================================================
// Function App Configuration
// ============================================================================

resource functionAppConfig 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: functionApp
  name: 'web'
  properties: {
    numberOfWorkers: 1
    defaultDocuments: []
    netFrameworkVersion: 'v6.0'
    requestTracingEnabled: true
    remoteDebuggingEnabled: false
    httpLoggingEnabled: true
    detailedErrorLoggingEnabled: true
    publishingUsername: '${functionAppName}'
    scmType: 'None'
    use32BitWorkerProcess: false
    webSocketsEnabled: false
    managedPipelineMode: 'Integrated'
    virtualApplications: [
      {
        virtualPath: '/'
        physicalPath: 'site\\wwwroot'
        preloadEnabled: true
      }
    ]
    loadBalancing: 'LeastRequests'
    experiments: {
      rampUpRules: []
    }
    autoHealEnabled: true
    localMySqlEnabled: false
    ipSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 1
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 1
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictionsUseMain: false
    http20Enabled: true
    minTlsVersion: '1.2'
    scmMinTlsVersion: '1.0'
    linuxFxVersion: 'DOCKER|${functionImageUri}'
  }
}

resource functionAppSettings 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: functionApp
  name: 'appsettings'
  properties: {
    AzureWebJobsStorage: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
    WEBSITE_CONTENTAZUREFILECONNECTIONSTRING: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
    WEBSITE_CONTENTSHARE: toLower(functionAppName)
    AzureWebJobsDisableHomePage: 'true'
    FUNCTIONS_WORKER_RUNTIME: 'python'
    FUNCTIONS_EXTENSION_RUNTIME_VERSION: '~4'
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
    APPLICATIONINSIGHTS_CONNECTION_STRING: 'InstrumentationKey=${appInsights.properties.InstrumentationKey}'
    
    // Database connection
    QAI_DB_CONN: 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Initial Catalog=${sqlDatabase.name};Persist Security Info=False;User ID=${sqlAdminUsername};Password=${sqlAdminPassword};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
    QAI_SQL_POOL_SIZE: '20'
    
    // Cosmos DB (if enabled)
    QAI_ENABLE_COSMOS: enableCosmos ? 'true' : 'false'
    COSMOS_ENDPOINT: enableCosmos ? cosmosAccount.properties.documentEndpoint : ''
    COSMOS_KEY: enableCosmos ? cosmosAccount.listKeys().primaryMasterKey : ''
    COSMOS_DATABASE: cosmosDbDatabaseName
    COSMOS_CONTAINER: cosmosDbContainerName
    
    // Default provider
    DEFAULT_AI_PROVIDER: 'local'
    OLLAMA_MODEL: 'qwen2.5-coder:7b'
    
    // Chat settings
    CHAT_TEMPERATURE: '0.7'
    CHAT_MAX_TOKENS: '2048'
    
    // Aria settings
    ARIA_PORT: '8080'
    ARIA_RENDER_MODE: 'ue5'
  }
}

// ============================================================================
// Diagnostic Settings
// ============================================================================

resource functionAppDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${functionAppName}-diagnostics'
  scope: functionApp
  properties: {
    workspaceId: appInsightsWorkspace.id
    logs: [
      {
        category: 'FunctionAppLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Function App URL')
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'

@description('Function App name')
output functionAppName string = functionApp.name

@description('SQL Server FQDN')
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName

@description('SQL Database name')
output sqlDatabaseName string = sqlDatabase.name

@description('Cosmos DB endpoint (if enabled)')
output cosmosDbEndpoint string = enableCosmos ? cosmosAccount.properties.documentEndpoint : ''

@description('Application Insights instrumentation key')
output appInsightsKey string = appInsights.properties.InstrumentationKey

@description('Storage account name')
output storageAccountName string = storageAccount.name

@description('Key Vault URI')
output keyVaultUri string = keyVault.properties.vaultUri

@description('Resource group name')
output resourceGroupName string = resourceGroup().name
