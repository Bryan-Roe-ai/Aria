CREATE TABLE [dbo].[OrchestratorJobs] (
    [OrchestratorJobId]    UNIQUEIDENTIFIER DEFAULT (newid()) NOT NULL,
    [OrchestratorType]     NVARCHAR (50)    NOT NULL,
    [JobName]              NVARCHAR (255)   NOT NULL,
    [ConfigYamlPath]       NVARCHAR (500)   NOT NULL,
    [Mode]                 NVARCHAR (100)   NULL,
    [IsDryRun]             BIT              DEFAULT ((0)) NOT NULL,
    [Status]               NVARCHAR (50)    DEFAULT ('pending') NOT NULL,
    [StartedAt]            DATETIME2 (7)    NULL,
    [CompletedAt]          DATETIME2 (7)    NULL,
    [ExecutionTimeSeconds] FLOAT (53)       NULL,
    [TrainingRunId]        UNIQUEIDENTIFIER NULL,
    [StatusJsonPath]       NVARCHAR (500)   NULL,
    [ErrorMessage]         NVARCHAR (MAX)   NULL,
    [OutputSummary]        NVARCHAR (MAX)   NULL,
    PRIMARY KEY CLUSTERED ([OrchestratorJobId] ASC)
);


GO

CREATE NONCLUSTERED INDEX [IX_OrchestratorJobs_JobName]
    ON [dbo].[OrchestratorJobs]([JobName] ASC);


GO

CREATE NONCLUSTERED INDEX [IX_OrchestratorJobs_Status]
    ON [dbo].[OrchestratorJobs]([Status] ASC);


GO

CREATE NONCLUSTERED INDEX [IX_OrchestratorJobs_Type]
    ON [dbo].[OrchestratorJobs]([OrchestratorType] ASC);


GO

CREATE NONCLUSTERED INDEX [IX_OrchestratorJobs_StartedAt]
    ON [dbo].[OrchestratorJobs]([StartedAt] DESC);


GO

