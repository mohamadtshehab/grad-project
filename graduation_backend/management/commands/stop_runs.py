from django.core.management.base import BaseCommand
from langsmith import Client
from dotenv import load_dotenv
import os
load_dotenv()

class Command(BaseCommand):
    help = 'Stop all running LangSmith runs for the grad-project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-name',
            type=str,
            default='grad-project',
            help='LangSmith project name (default: grad-project)'
        )
        parser.add_argument(
            '--run-id',
            type=str,
            help='Stop a specific run by ID'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be stopped without actually stopping'
        )

    def handle(self, *args, **options):
        # Load environment variables
        load_dotenv()
        
        try:
            # Initialize LangSmith client
            client = Client()
            project_name = options['project_name']
            
            if options['run_id']:
                # Stop specific run
                self.stop_specific_run(client, options['run_id'], options['dry_run'])
            else:
                # Stop all running runs
                self.stop_all_running_runs(client, project_name, options['dry_run'])
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error connecting to LangSmith: {e}")
            )
            self.stdout.write(
                self.style.WARNING("Make sure LANGCHAIN_API_KEY is set in your environment")
            )

    def stop_specific_run(self, client, run_id, dry_run=False):
        """Stop a specific run by ID."""
        try:
            if dry_run:
                self.stdout.write(f"[DRY RUN] Would stop run: {run_id}")
                return
            
            client.update_run(run_id=run_id, status="aborted")
            self.stdout.write(
                self.style.SUCCESS(f"Successfully stopped run: {run_id}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to stop run {run_id}: {e}")
            )

    def stop_all_running_runs(self, client, project_name, dry_run=False):
        """Stop all running runs in the project."""
        try:
            # Get all running runs
            filter_string = 'eq(status, "pending")'
            runs = list(client.list_runs(project_name=project_name, filter=filter_string))
            
            if not runs:
                self.stdout.write(
                    self.style.WARNING(f"No running runs found in project '{project_name}'")
                )
                return
            
            self.stdout.write(f"Found {len(runs)} running runs in project '{project_name}'")
            
            if dry_run:
                self.stdout.write("\n[DRY RUN] Would stop the following runs:")
                for run in runs:
                    self.stdout.write(f"  - Run ID: {run.id}")
                return
            
            # Stop each run
            stopped_count = 0
            failed_count = 0
            
            for run in runs:
                try:
                    self.stdout.write(f"Stopping run {run.id}...")
                    client.update_run(run_id=str(run.id), status="aborted")
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Run {run.id} stopped")
                    )
                    stopped_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Failed to stop run {run.id}: {e}")
                    )
                    failed_count += 1
            
            # Summary
            self.stdout.write("\n" + "="*50)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully stopped: {stopped_count} runs")
            )
            if failed_count > 0:
                self.stdout.write(
                    self.style.ERROR(f"Failed to stop: {failed_count} runs")
                )
            self.stdout.write("All operations completed!")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error listing runs: {e}")
            )
