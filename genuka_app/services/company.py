"""
Company Database Service for managing Company records
"""
from typing import Optional
from ..models import Company


class CompanyService:
    """Handles all database operations for the Company model"""

    def find_by_id(self, company_id: str) -> Optional[Company]:
        """
        Find company by ID.

        Args:
            company_id: Genuka company ID

        Returns:
            Company instance or None
        """
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None

    def find_by_handle(self, handle: str) -> Optional[Company]:
        """
        Find company by handle.

        Args:
            handle: Company handle

        Returns:
            Company instance or None
        """
        try:
            return Company.objects.get(handle=handle)
        except Company.DoesNotExist:
            return None

    def find_by_access_token(self, access_token: str) -> Optional[Company]:
        """
        Find company by access token.

        Args:
            access_token: OAuth access token

        Returns:
            Company instance or None
        """
        try:
            return Company.objects.get(access_token=access_token)
        except Company.DoesNotExist:
            return None

    def find_all(self) -> list:
        """
        Get all companies.

        Returns:
            List of Company instances
        """
        return list(Company.objects.all().order_by('-created_at'))

    def upsert_company(self, data: dict) -> Company:
        """
        Create or update company.

        Args:
            data: Dictionary with company data

        Returns:
            Company instance
        """
        company_id = data.pop('id')

        company, created = Company.objects.update_or_create(
            id=company_id,
            defaults=data
        )

        return company

    def update_by_id(self, company_id: str, data: dict) -> Optional[Company]:
        """
        Update company by ID.

        Args:
            company_id: Genuka company ID
            data: Dictionary with fields to update

        Returns:
            Updated Company instance or None
        """
        try:
            company = Company.objects.get(id=company_id)
            for key, value in data.items():
                setattr(company, key, value)
            company.save()
            return company
        except Company.DoesNotExist:
            return None

    def delete_by_id(self, company_id: str) -> bool:
        """
        Delete company by ID.

        Args:
            company_id: Genuka company ID

        Returns:
            True if deleted, False if not found
        """
        try:
            company = Company.objects.get(id=company_id)
            company.delete()
            return True
        except Company.DoesNotExist:
            return False
