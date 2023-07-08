import {
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
	registerDecorator,
} from 'class-validator';
import { DataService } from './data.service';
import { Inject, Injectable, forwardRef } from '@nestjs/common';

export function IsDataExistedByHashValue(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			name: 'isDataExisted',
			target: object.constructor,
			propertyName,
			options: validationOptions,
			validator: IsDataExistedByHashValueConstraint,
		});
	};
}

@ValidatorConstraint({ async: true, name: 'IsDataExistedByHashValueConstraint' })
@Injectable()
export class IsDataExistedByHashValueConstraint implements ValidatorConstraintInterface {
	constructor(
		@Inject(forwardRef(() => DataService))
		private readonly dataService: DataService,
	) {}

	async validate(value: any) {
		const result = await this.dataService.findOneBy({ hashValue: value });
		return result == null;
	}
}
