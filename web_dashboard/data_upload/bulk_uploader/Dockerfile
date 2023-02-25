FROM mcr.microsoft.com/dotnet/core/sdk:3.1

WORKDIR /tmp

RUN dotnet new console -o ScenarioUploader

WORKDIR /tmp/ScenarioUploader
RUN dotnet add package Microsoft.Azure.Cosmos

RUN rm Program.cs
ADD ScenarioUploader.cs /tmp/ScenarioUploader/

RUN dotnet publish -c Release -o /app

WORKDIR /app

ENTRYPOINT ["dotnet", "ScenarioUploader.dll"]
