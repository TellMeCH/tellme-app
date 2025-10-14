# TODO: Service Account as ${{ vars.SERVICE_NAME }}-account@${{ secrets.GCP_PROJECT_ID }}.iam.gserviceaccount.com
# TODO: Image Url as ${{ secrets.GCP_PROJECT_REGION }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/${{ vars.ARTIFACT_REPO }}/${{ vars.SERVICE_NAME }}:${{ github.sha }}
# TODO: CloudSQL as ${{ secrets.GCP_PROJECT_ID }}:${{ secrets.GCP_PROJECT_REGION }}:${{ vars.SQL_INSTANCE_NAME }}

variable "service_name" {
  type = string
}

variable "image_url" {
  type = string
}

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "service_account_email" {
  type = string
}

variable "cloud_sql" {
  type = string
}