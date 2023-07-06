import {
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
	registerDecorator,
} from 'class-validator';
import { hash } from 'bcrypt';
import { DataService } from './data.service';

@ValidatorConstraint({ async: true })
export class IsDataExistedConstraint implements ValidatorConstraintInterface {
	constructor(private readonly dataService: DataService) {}
	validate(value: string) {
		return this.dataService
			.findOneBy({ hashValue: hash(value, 12) as unknown as string })
			.then((data) => {
				return !data;
			});
	}
}

export function IsDataExisted(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			target: object.constructor,
			propertyName: propertyName,
			options: validationOptions,
			constraints: [],
			validator: IsDataExistedConstraint,
		});
	};
}
