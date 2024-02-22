#include<stdio.h>
void main() 
{
int list[10], i,j, n;
printf("Enter the size of the array: ");
scanf("%d", &n);
printf("Enter the array elements: ");
for (i = 0; i < n; i++) 
    scanf("%d", &list[i]);
int ele;
printf("Enter the element to be searched: ");
scanf("%d", &ele);
for(i=0;i<n-1;i++)
{
    for(j=0;j<n-i-1;j++)
    {
        if(list[j]>list[j+1])
        {
            int temp = list[j];
            list[j] = list[j+1];
            list[j+1] = temp; 
        }
    }
}
int left=0;
int right=n-1;
int middle;
while (left <= right) {
middle = (left + right) / 2;
if (ele == list[middle]) {
  printf("The element %d is found at index %d.\n", ele, middle);
  break;
}
else if (ele < list[middle])
  right = middle - 1;
else 
  left = middle + 1;

}
if (left > right) 
printf("The element %d is not found in the array.\n", ele);

}
