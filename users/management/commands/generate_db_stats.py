from django.core.management.base import BaseCommand
from django.db.models import Count
from users.models import User
from projects.models import Project, Home, BluePrint
from inspections.models import Inspection, HomeInspection, Deficiency, DefImage
from datetime import datetime
import os


class Command(BaseCommand):
    help = "Generates a text file containing database statistics"

    def handle(self, *args, **options):
        # Get the current timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"db_stats_{timestamp}.txt"

        # Create the stats directory if it doesn't exist
        stats_dir = "db_stats"
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir)

        filepath = os.path.join(stats_dir, filename)

        with open(filepath, "w") as f:
            f.write("Database Statistics Report\n")
            f.write("=" * 50 + "\n\n")

            # Users statistics
            f.write("Users Statistics:\n")
            f.write("-" * 20 + "\n")
            total_users = User.objects.count()
            f.write(f"Total Users: {total_users}\n\n")

            # Projects statistics
            f.write("Projects Statistics:\n")
            f.write("-" * 20 + "\n")
            total_projects = Project.objects.count()
            f.write(f"Total Projects: {total_projects}\n\n")

            # Homes statistics
            f.write("Homes Statistics:\n")
            f.write("-" * 20 + "\n")
            total_homes = Home.objects.count()
            f.write(f"Total Homes: {total_homes}\n\n")

            # BluePrints statistics
            f.write("BluePrints Statistics:\n")
            f.write("-" * 20 + "\n")
            total_blueprints = BluePrint.objects.count()
            f.write(f"Total BluePrints: {total_blueprints}\n\n")

            # Inspections statistics
            f.write("Inspections Statistics:\n")
            f.write("-" * 20 + "\n")
            total_inspections = Inspection.objects.count()
            f.write(f"Total Inspections: {total_inspections}\n\n")

            # Home Inspections statistics
            f.write("Home Inspections Statistics:\n")
            f.write("-" * 20 + "\n")
            total_home_inspections = HomeInspection.objects.count()
            f.write(f"Total Home Inspections: {total_home_inspections}\n\n")

            # Deficiencies statistics
            f.write("Deficiencies Statistics:\n")
            f.write("-" * 20 + "\n")
            total_deficiencies = Deficiency.objects.count()
            f.write(f"Total Deficiencies: {total_deficiencies}\n\n")

            # Deficiency Images statistics
            f.write("Deficiency Images Statistics:\n")
            f.write("-" * 20 + "\n")
            total_def_images = DefImage.objects.count()
            f.write(f"Total Deficiency Images: {total_def_images}\n\n")

            # Add timestamp
            f.write(
                f'\nReport generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated database statistics in {filepath}"
            )
        )
